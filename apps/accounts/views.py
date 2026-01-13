from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import logout, authenticate
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy
from django.views import View
from django.http import HttpResponseRedirect
from apps.courses.models import Course, Enrollment
from apps.payments.models import Payment
from .forms import UserRegistrationForm, UserUpdateForm, ProfileUpdateForm
from apps.accounts.tasks import send_activation_email_task
from django.core.exceptions import ValidationError


class CustomAuthenticationForm(AuthenticationForm):
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            self.user_cache = authenticate(
                self.request, 
                username=username, 
                password=password
            )
            if self.user_cache is None:
                # the username exists or the password is wrong
                raise self.get_invalid_login_error()
            elif not self.user_cache.is_active:
                raise self.get_inactive_login_error()
        return self.cleaned_data

    def get_invalid_login_error(self):
        # Generic error message to prevent username enumeration
        message = gettext_lazy("Invalid username or password. Please try again")
        return ValidationError(
            message,
            code='invalid_login',
            params={'username': self.username_field.verbose_name},
        )
        
    def get_inactive_login_error(self):
        return ValidationError(
            self.error_messages['inactive'],
            code='inactive',
        )


class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    
    def get_success_url(self):
        user = self.request.user
        if user.is_superuser or (hasattr(user, 'profile') and user.profile.is_admin()):
            return reverse_lazy('admin:index')
        elif hasattr(user, 'profile') and user.profile.is_instructor():
            return reverse_lazy('accounts:profile')
        else:
            return reverse_lazy('user_dashboard')

    # @method_decorator(ratelimit(key='ip', rate='5/5m', method='POST', block=False))
    def post(self, request, *args, **kwargs):
        # Check if rate limited
        if getattr(request, 'limited', False):
            messages.error(
                request,
                'Too many login attempts. Please try again in 5 minutes.'
            )
            return redirect('accounts:login')
        return super().post(request, *args, **kwargs)


class CustomLogoutView(View):
    def get(self, request):
        return self.post(request)
        
    def post(self, request):
        logout(request)
        # Check if user is admin (superuser or admin role)
        if (hasattr(request.user, 'is_superuser') and request.user.is_superuser) or (
                hasattr(request.user, 'profile') and request.user.profile.is_admin()):
            # Redirect admin to home page
            return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect(reverse_lazy('courses:home'))


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Send activation email asynchronously
            current_site = get_current_site(request)
            protocol = 'https' if request.is_secure() else 'http'
            send_activation_email_task.delay(user.id, current_site.domain, protocol)
            
            messages.success(request, 'Registration successful. Please check your email for activation instructions.')
            return redirect('accounts:login')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request):
    # Check if user is admin and redirect to Django admin
    if request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_admin()):
        return redirect('admin:index')
    
    # Get user role
    user_role = getattr(request.user.profile, 'role', 'student')
    
    context = {}
    
    if user_role == 'student':
        # Student dashboard
        enrollments = request.user.enrollments.all()
        payments = Payment.objects.filter(user=request.user).order_by('-created_at')
        context['enrollments'] = enrollments
        context['payments'] = payments
    elif user_role == 'instructor':
        # Instructor dashboard
        courses = Course.objects.filter(instructor=request.user)
        # Fetch enrollments for courses taught by this instructor
        enrollments = Enrollment.objects.filter(course__instructor=request.user).select_related('user', 'course').order_by('-enrolled_at')
        context['courses'] = courses
        context['enrollments'] = enrollments
    elif user_role == 'admin':
        # Admin dashboard
        total_students = User.objects.students().count()
        total_instructors = User.objects.instructors().count()
        total_courses = Course.objects.count()
        context['total_students'] = total_students
        context['total_instructors'] = total_instructors
        context['total_courses'] = total_courses
    else:
        # Default to student dashboard
        enrollments = request.user.enrollments.all()
        payments = Payment.objects.filter(user=request.user).order_by('-created_at')
        context['enrollments'] = enrollments
        context['payments'] = payments
    
    template = 'accounts/user_dashboard.html'
    
    return render(request, template, context)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('edit_profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'u_form': u_form,
        'p_form': p_form}
    
    return render(request, 'accounts/edit_profile.html', context)
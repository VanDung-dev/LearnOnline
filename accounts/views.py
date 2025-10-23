from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from courses.models import Course, Enrollment
from .forms import UserRegistrationForm, UserUpdateForm, ProfileUpdateForm


class CustomLoginView(LoginView):
    def get_success_url(self):
        user = self.request.user
        if user.is_superuser or (hasattr(user, 'profile') and user.profile.is_admin()):
            return reverse_lazy('admin:index')
        elif hasattr(user, 'profile') and user.profile.is_instructor():
            return reverse_lazy('accounts:profile')
        else:
            return reverse_lazy('courses:home')


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful. You can now log in.')
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
        context['enrollments'] = enrollments
        template = 'accounts/student_dashboard.html'
    elif user_role == 'instructor':
        # Instructor dashboard
        courses = Course.objects.filter(instructor=request.user)
        context['courses'] = courses
        template = 'accounts/instructor_dashboard.html'
    elif user_role == 'admin':
        # Admin dashboard
        total_students = User.objects.students().count()
        total_instructors = User.objects.instructors().count()
        total_courses = Course.objects.count()
        context['total_students'] = total_students
        context['total_instructors'] = total_instructors
        context['total_courses'] = total_courses
        template = 'accounts/admin_dashboard.html'
    else:
        # Default to student dashboard
        enrollments = request.user.enrollments.all()
        context['enrollments'] = enrollments
        template = 'accounts/student_dashboard.html'
    
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
            return redirect('accounts:edit_profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    
    return render(request, 'accounts/edit_profile.html', context)
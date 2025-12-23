from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.db.models import Count, Prefetch
from apps.courses.models import Course, Enrollment
from .models import Discussion, Reply
from .forms import DiscussionForm, ReplyForm

class CourseContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_slug = self.kwargs.get('slug')
        context['course'] = get_object_or_404(Course, slug=course_slug)
        context['is_instructor'] = context['course'].instructor == self.request.user
        return context

class DiscussionListView(LoginRequiredMixin, CourseContextMixin, ListView):
    model = Discussion
    template_name = 'discussions/list.html'
    context_object_name = 'discussions'
    paginate_by = 10

    def get_queryset(self):
        course_slug = self.kwargs.get('slug')
        return Discussion.objects.filter(course__slug=course_slug).select_related('author').annotate(reply_count=Count('replies'))

class DiscussionCreateView(LoginRequiredMixin, CourseContextMixin, CreateView):
    model = Discussion
    form_class = DiscussionForm
    template_name = 'discussions/create.html'

    def form_valid(self, form):
        course = get_object_or_404(Course, slug=self.kwargs.get('slug'))
        # Check enrollment
        if course.instructor != self.request.user and not Enrollment.objects.filter(course=course, user=self.request.user).exists():
            messages.error(self.request, "You must be enrolled to post discussions.")
            return redirect('courses:course_detail', slug=course.slug)
            
        form.instance.course = course
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('discussions:discussion_list', kwargs={'slug': self.kwargs.get('slug')})

class DiscussionDetailView(LoginRequiredMixin, CourseContextMixin, DetailView):
    model = Discussion
    template_name = 'discussions/detail.html'
    context_object_name = 'discussion'

    def get_queryset(self):
        # Optimization: Prefetch replies and specific votes
        return super().get_queryset().select_related('author').prefetch_related(
            'replies', 'replies__author'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reply_form'] = ReplyForm()
        # Pass user id to template for JS
        context['user_id'] = self.request.user.id
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.discussion = self.object
            reply.author = request.user
            reply.save()
            messages.success(request, "Reply posted successfully.")
            return redirect('discussions:discussion_detail', slug=self.kwargs.get('slug'), pk=self.object.pk)
        return self.render_to_response(self.get_context_data(reply_form=form))


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
    template_name = 'discussions/discussions_list.html'
    context_object_name = 'discussions'
    paginate_by = 10

    def get_queryset(self):
        course_slug = self.kwargs.get('slug')
        return Discussion.objects.filter(course__slug=course_slug).select_related('author').annotate(reply_count=Count('replies'))

class DiscussionCreateView(LoginRequiredMixin, CourseContextMixin, CreateView):
    model = Discussion
    form_class = DiscussionForm
    template_name = 'discussions/create_discussions.html'

    def form_valid(self, form):
        course = get_object_or_404(Course, slug=self.kwargs.get('slug'))
        # Check enrollment
        if course.instructor != self.request.user and not Enrollment.objects.filter(course=course, user=self.request.user).exists():
            messages.error(self.request, "You must be enrolled to post discussions.")
            return redirect('courses:course_detail', slug=course.slug)
            
        form.instance.course = course
        form.instance.author = self.request.user
        response = super().form_valid(form)
        
        # Notify instructor if the author is not the instructor
        if course.instructor != self.request.user:
            from apps.notifications.models import Notification
            Notification.objects.create(
                recipient=course.instructor,
                sender=self.request.user,
                title=f"New Discussion: {form.instance.title}",
                message=f"{self.request.user.username} started a new discussion in {course.title}.",
                link=reverse('discussions:discussion_detail', kwargs={'slug': course.slug, 'pk': self.object.pk}),
                notification_type='discussion'
            )
            
        return response

    def get_success_url(self):
        return reverse('discussions:discussion_list', kwargs={'slug': self.kwargs.get('slug')})

class DiscussionDetailView(LoginRequiredMixin, CourseContextMixin, DetailView):
    model = Discussion
    template_name = 'discussions/discussions_detail.html'
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

        # Handle Discussion Edit
        if 'edit_discussion' in request.POST:
            if self.object.author != request.user:
                messages.error(request, "You are not allowed to edit this discussion.")
                return redirect('discussions:discussion_detail', slug=self.kwargs.get('slug'), pk=self.object.pk)
            
            new_body = request.POST.get('body')
            new_title = request.POST.get('title')
            
            if new_body:
                self.object.body = new_body
            
            if new_title:
                self.object.title = new_title
                
            self.object.save()
            messages.success(request, "Discussion updated successfully.")
            return redirect('discussions:discussion_detail', slug=self.kwargs.get('slug'), pk=self.object.pk)

        # Handle Reply Edit
        if 'edit_reply' in request.POST:
            reply_id = request.POST.get('reply_id')
            reply = get_object_or_404(Reply, id=reply_id)
            if reply.author != request.user:
                messages.error(request, "You are not allowed to edit this reply.")
                return redirect('discussions:discussion_detail', slug=self.kwargs.get('slug'), pk=self.object.pk)
            
            new_body = request.POST.get('body')
            if new_body:
                reply.body = new_body
                reply.save()
                messages.success(request, "Reply updated successfully.")
            return redirect('discussions:discussion_detail', slug=self.kwargs.get('slug'), pk=self.object.pk)

        # Handle New Reply
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.discussion = self.object
            reply.author = request.user
            reply.save()
            
            # Notify discussion author (if reply author is not discussion author)
            from apps.notifications.models import Notification
            if self.object.author != request.user:
                Notification.objects.create(
                    recipient=self.object.author,
                    sender=request.user,
                    title=f"New Reply in: {self.object.title}",
                    message=f"{request.user.username} replied to your discussion.",
                    link=reverse('discussions:discussion_detail', kwargs={'slug': self.kwargs.get('slug'), 'pk': self.object.pk}),
                    notification_type='discussion'
                )
            
            # Notify instructor (if reply author is not instructor and instructor is not discussion author - already notified above)
            course = self.object.course
            if course.instructor != request.user and course.instructor != self.object.author:
                 Notification.objects.create(
                    recipient=course.instructor,
                    sender=request.user,
                    title=f"New Reply in: {self.object.title}",
                    message=f"{request.user.username} replied to a discussion in {course.title}.",
                    link=reverse('discussions:discussion_detail', kwargs={'slug': self.kwargs.get('slug'), 'pk': self.object.pk}),
                    notification_type='discussion'
                )
            messages.success(request, "Reply posted successfully.")
            return redirect('discussions:discussion_detail', slug=self.kwargs.get('slug'), pk=self.object.pk)
        return self.render_to_response(self.get_context_data(reply_form=form))


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, Http404
from django.contrib import messages
from django.db import models
from django.utils import timezone
from django.db.models import Q
from ..models import Course, Enrollment
from ..forms import CourseForm

@login_required
def create_course(request):
    if not hasattr(request.user, 'profile') or not request.user.profile.is_instructor():
        return HttpResponseForbidden("You must be an instructor to create courses.")

    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            messages.success(request, 'Course created successfully!')
            return redirect('courses:instructor_courses')
    else:
        form = CourseForm()

    context = {
        'form': form,
    }
    return render(request, 'courses/create_course.html', context)


@login_required
def edit_course(request, slug):
    course = get_object_or_404(Course, slug=slug, instructor=request.user)

    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully!')
            return redirect('courses:instructor_courses')
    else:
        form = CourseForm(instance=course)

    context = {
        'form': form,
        'course': course,
    }
    return render(request, 'courses/edit_course.html', context)


@login_required
def delete_course(request, slug):
    course = get_object_or_404(Course, slug=slug, instructor=request.user)

    if request.method == 'POST':
        course_title = course.title
        course.delete()
        messages.success(request, f'Course "{course_title}" has been deleted successfully!')
        return redirect('courses:instructor_courses')

    # Instead of rendering a separate template, redirect to edit_course with a delete flag
    return redirect('courses:edit_course', slug=slug)


def course_list(request):
    # Only show courses that are currently open
    now = timezone.now()
    courses = Course.objects.filter(is_active=True)

    # Filter courses to exclude those that have closed
    courses = courses.filter(
        models.Q(closing_date__isnull=True) | models.Q(closing_date__gte=now)
    )

    # Handle search
    query = request.GET.get('q')
    if query:
        courses = courses.filter(
            Q(title__icontains=query) |
            Q(short_description__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(instructor__username__icontains=query) |
            Q(instructor__first_name__icontains=query) |
            Q(instructor__last_name__icontains=query)
        ).distinct()

    context = {
        'courses': courses,
        'query': query,
    }
    return render(request, 'courses/course_list.html', context)


def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug, is_active=True)

    # Check if course is currently available for viewing (not closed)
    now = timezone.now()
    if course.closing_date and now > course.closing_date:
        # Course has closed
        raise Http404("Course is not currently available")

    # Check if user is enrolled in the course
    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()

    context = {
        'course': course,
        'is_enrolled': is_enrolled,
    }
    return render(request, 'courses/course_detail.html', context)


@login_required
def preview_course(request, slug):
    # Allow instructors to preview their courses as if they were students
    course = get_object_or_404(Course, slug=slug)
    
    # Check if user is the instructor of this course
    if request.user != course.instructor:
        return HttpResponseForbidden("You are not authorized to preview this course.")
    
    # For preview purposes, treat instructor as enrolled
    is_enrolled = True
    
    context = {
        'course': course,
        'is_enrolled': is_enrolled,
        'is_preview': True,  # Flag to indicate this is a preview
    }
    return render(request, 'courses/course_detail.html', context)
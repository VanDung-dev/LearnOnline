from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.db import models
from django.utils import timezone
from ..models import Course, Lesson, Enrollment, Module, Category


def home(request):
    categories = Category.objects.all()
    # Show all active courses (regardless of opening date) but respect closing date
    now = timezone.now()
    courses = Course.objects.filter(is_active=True)
    # Filter courses to exclude those that have closed
    courses = courses.filter(
        models.Q(closing_date__isnull=True) | models.Q(closing_date__gte=now)
    )[:6]

    context = {
        'categories': categories,
        'courses': courses,
    }
    return render(request, 'courses/home.html', context)


# Custom 404 view
def custom_page_not_found(request, exception):
    print("Custom 404 view called")  # Debug print
    print(f"Exception: {exception}")  # Debug print
    return render(request, '404.html', status=404)


@login_required
def enroll_course(request, slug):
    course = get_object_or_404(Course, slug=slug, is_active=True)

    # Check if course is currently open for enrollment
    now = timezone.now()
    if course.closing_date and now > course.closing_date:
        messages.error(request, "Enrollment for this course is closed.")
        return redirect('courses:course_detail', slug=slug)

    # Check if user is already enrolled
    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user,
        course=course
    )

    if created:
        messages.success(request, "You have been successfully enrolled in this course.")
    else:
        messages.info(request, "You are already enrolled in this course.")

    return render(request, 'courses/enrollment_success.html', {'course': course})


@login_required
def instructor_courses(request):
    if not hasattr(request.user, 'profile') or not request.user.profile.is_instructor():
        return HttpResponseForbidden("You must be an instructor to view this page.")

    courses = Course.objects.filter(instructor=request.user)
    context = {
        'courses': courses,
    }
    return render(request, 'courses/instructor_courses.html', context)


@login_required
def delete_lesson_video(request, course_slug, module_id, lesson_id):
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    module = get_object_or_404(Module, id=module_id, course=course)
    lesson = get_object_or_404(Lesson, id=lesson_id, module=module)

    if request.method == 'POST':
        # Check if lesson has a video file
        if lesson.video_file:
            # Delete the video file
            lesson.video_file.delete()
            lesson.video_file = None
            lesson.save()
            messages.success(request, 'Video file deleted successfully!')
        else:
            messages.info(request, 'No video file found for this lesson.')

    return redirect('courses:edit_course', slug=course.slug)


@login_required
def configure_quiz(request, lesson_id=None):
    """
    Redirect to the edit lesson page where quiz configuration is now handled
    """
    if lesson_id:
        lesson = get_object_or_404(Lesson, id=lesson_id, module__course__instructor=request.user)
        # Redirect to the edit lesson page where quiz configuration is now handled
        return redirect('courses:edit_lesson', course_slug=lesson.module.course.slug, module_id=lesson.module.id, lesson_id=lesson.id)
    else:
        # Handle standalone quiz creation/configuration - redirect to instructor courses
        messages.info(request, "Quiz configuration is now handled directly in the lesson editing page.")
        return redirect('courses:instructor_courses')
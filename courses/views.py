from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, Http404
from django.contrib import messages
from django.db import models
from django.utils import timezone
from .models import Category, Course, Lesson, Enrollment, Progress, Module, Certificate
from .forms import CourseForm, ModuleForm, LessonForm


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


def course_list(request):
    # Only show courses that are currently open
    now = timezone.now()
    courses = Course.objects.filter(is_active=True)

    # Filter courses to exclude those that have closed
    courses = courses.filter(
        models.Q(closing_date__isnull=True) | models.Q(closing_date__gte=now)
    )
    context = {
        'courses': courses,
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
def lesson_detail(request, course_slug, lesson_slug):
    course = get_object_or_404(Course, slug=course_slug, is_active=True)
    lesson = get_object_or_404(Lesson, slug=lesson_slug, module__course=course)
    
    # Check if course is currently open
    now = timezone.now()
    if ((course.opening_date and now < course.opening_date) or 
        (course.closing_date and now > course.closing_date)):
        raise Http404("Course is not currently available")
    
    # Check if user is enrolled in the course
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
    is_enrolled = True
    
    # Mark lesson as completed
    progress, created = Progress.objects.get_or_create(
        user=request.user,
        lesson=lesson
    )
    
    if not progress.completed:
        progress.completed = True
        progress.save()
    
    # Check if course is completed and issue certificate if needed
    check_and_issue_certificate(request.user, course)
    
    # Get next and previous lessons
    all_lessons = Lesson.objects.filter(module__course=course, is_published=True)
    current_index = list(all_lessons).index(lesson)
    
    prev_lesson = None
    next_lesson = None
    
    if current_index > 0:
        prev_lesson = all_lessons[current_index - 1]
    
    if current_index < len(all_lessons) - 1:
        next_lesson = all_lessons[current_index + 1]
    
    context = {
        'course': course,
        'lesson': lesson,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
        'enrollment': enrollment,
    }
    return render(request, 'courses/lesson_detail.html', context)


def check_and_issue_certificate(user, course):
    """
    Check if user has completed all lessons in a course and issue certificate if so
    """
    # Get all lessons in the course
    all_lessons = Lesson.objects.filter(module__course=course, is_published=True)
    total_lessons = all_lessons.count()
    
    if total_lessons == 0:
        return  # No lessons to complete
    
    # Get completed lessons for this user in this course
    completed_lessons = Progress.objects.filter(
        user=user,
        lesson__in=all_lessons,
        completed=True
    ).count()
    
    # Check if all lessons are completed
    if completed_lessons == total_lessons:
        # Get enrollment
        enrollment = get_object_or_404(Enrollment, user=user, course=course)
        
        # Mark enrollment as completed
        if not enrollment.is_completed:
            enrollment.is_completed = True
            enrollment.save()
        
        # Check if the course has expired
        if course.expiration_date and timezone.now() > course.expiration_date:
            # Course has expired, don't issue certificate
            return
        
        # Create certificate if it doesn't exist and course hasn't expired
        certificate, created = Certificate.objects.get_or_create(
            user=user,
            course=course,
            enrollment=enrollment
        )
        
        if created:
            # Notify user about certificate
            pass  # We could send a message here if needed


# Instructor views
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
    
    context = {
        'course': course,
    }
    return render(request, 'courses/delete_course.html', context)


@login_required
def create_module(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    
    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.course = course
            module.save()
            messages.success(request, 'Module created successfully!')
            return redirect('courses:edit_course', slug=course.slug)
    else:
        form = ModuleForm()
    
    context = {
        'form': form,
        'course': course,
    }
    return render(request, 'courses/create_module.html', context)


@login_required
def edit_module(request, course_slug, module_id):
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    module = get_object_or_404(Module, id=module_id, course=course)
    
    if request.method == 'POST':
        form = ModuleForm(request.POST, instance=module)
        if form.is_valid():
            form.save()
            messages.success(request, 'Module updated successfully!')
            return redirect('courses:edit_course', slug=course.slug)
    else:
        form = ModuleForm(instance=module)
    
    context = {
        'form': form,
        'course': course,
        'module': module,
    }
    return render(request, 'courses/edit_module.html', context)


@login_required
def create_lesson(request, course_slug, module_id):
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    module = get_object_or_404(Module, id=module_id, course=course)
    
    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.module = module
            lesson.save()
            messages.success(request, 'Lesson created successfully!')
            return redirect('courses:edit_course', slug=course.slug)
    else:
        form = LessonForm()
    
    context = {
        'form': form,
        'course': course,
        'module': module,
    }
    return render(request, 'courses/create_lesson.html', context)


@login_required
def course_certificate(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    certificate = get_object_or_404(Certificate, user=request.user, course=course)
    
    context = {
        'certificate': certificate,
    }
    return render(request, 'courses/certificate.html', context)
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from django.utils import timezone
from ..models import Category, Course, Lesson, Enrollment, Certificate


def public_certificate(request, certificate_id):
    """
    Public view for certificate verification.
    Anyone with the certificate ID can view the certificate.
    """
    certificate = get_object_or_404(Certificate, certificate_number=certificate_id)

    context = {
        'certificate': certificate,
        'is_public': True,
    }
    return render(request, 'courses/certificate.html', context)


@login_required
def purchase_certificate(request, slug):
    """
    Redirect to payment system for certificate purchase
    """
    course = get_object_or_404(Course, slug=slug)

    # Check if user is enrolled in the course
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)

    # Check if certificate is free
    if course.is_certificate_free():
        messages.info(request, "Certificate is free for this course.")
        first_module = course.modules.first()
        if first_module:
            first_lesson = first_module.lessons.first()
            if first_lesson:
                return redirect('courses:lesson_detail', course_slug=course.slug, lesson_slug=first_lesson.slug)

    # Redirect to payment system
    return redirect('payments:purchase_certificate_payment', course_slug=slug)


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


def course_certificate(request, certificate_id):
    """
    View for certificate verification.
    If user is authenticated, they can view their own certificate.
    For public access, anyone with the certificate ID can view the certificate.
    """
    certificate = get_object_or_404(Certificate, certificate_number=certificate_id)

    # Check if user is authenticated and owns this certificate
    is_owner = request.user.is_authenticated and certificate.user == request.user

    context = {
        'certificate': certificate,
        'is_public': not is_owner,
    }
    return render(request, 'courses/certificate.html', context)


# Custom 404 view
def custom_page_not_found(request, exception):
    print("Custom 404 view called")  # Debug print
    print(f"Exception: {exception}")  # Debug print
    return render(request, '404.html', status=404)
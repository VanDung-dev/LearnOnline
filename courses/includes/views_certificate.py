from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Course, Enrollment, Certificate


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
"""
Certificate Service - Business logic for Certificate generation

This layer contains all business logic for Certificate management,
separated from views for better testability and reusability.
"""
from typing import Optional
from django.contrib.auth.models import User

from ..models import Course, Certificate, Enrollment


def can_generate_certificate(user: User, course: Course) -> bool:
    """Check if user is eligible for certificate"""
    # User must be enrolled
    enrollment = Enrollment.objects.filter(user=user, course=course).first()
    if not enrollment:
        return False

    # Course must be 100% completed
    total_lessons = course.sections.prefetch_related('subsections__lessons').count()
    if total_lessons == 0:
        return False

    completed_lessons = course.sections.filter(
        subsections__lessons__progress_records__user=user,
        subsections__lessons__progress_records__completed=True
    ).count()

    return completed_lessons >= total_lessons


def generate_certificate(user: User, course: Course) -> Certificate:
    """Generate certificate for user"""
    if not can_generate_certificate(user, course):
        raise ValueError("User is not eligible for certificate")

    enrollment = Enrollment.objects.get(user=user, course=course)

    certificate, created = Certificate.objects.get_or_create(
        user=user,
        course=course,
        enrollment=enrollment
    )

    return certificate


def get_certificate(user: User, course: Course) -> Optional[Certificate]:
    """Get existing certificate for user and course"""
    return Certificate.objects.filter(user=user, course=course).first()


def get_user_certificates(user: User):
    """Get all certificates for a user"""
    return Certificate.objects.filter(user=user).select_related('course').order_by('-issued_at')

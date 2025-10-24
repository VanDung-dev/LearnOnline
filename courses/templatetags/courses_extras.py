from django import template
from django.utils import timezone
from ..models import Certificate, Enrollment

register = template.Library()

@register.filter
def has_certificate(user, course):
    """
    Check if user has a certificate for a specific course
    """
    if not user.is_authenticated:
        return False
    return Certificate.objects.filter(user=user, course=course).exists()

@register.filter
def is_course_completed(user, course):
    """
    Check if user has completed a course (all lessons)
    """
    if not user.is_authenticated:
        return False
    
    # Get all lessons in the course
    all_lessons = course.modules.values_list('lessons', flat=True)
    
    if not all_lessons.exists():
        return False
    
    # Count completed lessons
    completed_lessons = user.progress_records.filter(
        lesson__in=all_lessons,
        completed=True
    ).count()
    
    return completed_lessons == all_lessons.count()

@register.filter
def is_course_expired(course):
    """
    Check if a course has expired
    """
    if not course.expiration_date:
        return False
    return timezone.now() > course.expiration_date

@register.simple_tag
def module_deadline(module, user):
    """
    Get the deadline for a module based on user's enrollment date
    """
    if not user.is_authenticated:
        return None
    
    try:
        enrollment = Enrollment.objects.get(user=user, course=module.course)
        return module.get_deadline(enrollment.enrolled_at)
    except Enrollment.DoesNotExist:
        return module.get_deadline()
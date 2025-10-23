from django import template
from ..models import Certificate

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
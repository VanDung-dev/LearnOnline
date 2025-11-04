import os
from django import template
from django.utils import timezone
from ..models import Certificate, Enrollment

register = template.Library()

@register.filter(name='basename')
def basename_filter(path):
    return os.path.basename(str(path))

@register.filter
def has_certificate(user, course):
    """
    Check if user has a certificate for a specific course
    """
    if not user.is_authenticated:
        return False
    return Certificate.objects.filter(user=user, course=course).exists()

@register.filter
def get_certificate(user, course):
    """
    Get the certificate object for a user in a specific course
    """
    if not user.is_authenticated:
        return None
    try:
        return Certificate.objects.get(user=user, course=course)
    except Certificate.DoesNotExist:
        return None

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

@register.filter
def course_duration_weeks(course):
    """
    Calculate the total duration of a course in weeks based on module durations
    """
    total_days = sum(module.duration_days for module in course.modules.all())
    weeks = total_days / 7.0
    return round(weeks, 1) if weeks % 1 != 0 else int(weeks)

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

@register.filter
def youtube_embed_url(url):
    """
    Convert YouTube URL to embed format
    """
    if not url:
        return ''
        
    # Handle various YouTube URL formats
    import re
    
    # Regex pattern to match YouTube URLs and extract video ID
    patterns = [
        r'(?:v=|be\/|embed\/|v\/|watch\?.*v=)([\w-]{11})',
        r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([\w-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            break
    else:
        video_id = None
    
    if video_id:
        # Make sure we return a proper embed URL
        return f'https://www.youtube.com/embed/{video_id}'
        
    # Return original URL if not a recognized YouTube format
    return url
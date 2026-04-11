"""
Progress Service - Business logic for Progress tracking

This layer contains all business logic for student progress tracking,
separated from views for better testability and reusability.
"""
from typing import Optional, Dict, Any
from django.contrib.auth.models import User
from django.utils import timezone

from ..models import Lesson, Progress, Enrollment, Course


def get_user_lesson_progress(user: User, lesson: Lesson) -> Optional[Progress]:
    """Get user progress for a specific lesson"""
    return Progress.objects.filter(user=user, lesson=lesson).first()


def mark_lesson_completed(user: User, lesson: Lesson) -> Progress:
    """Mark a lesson as completed for user"""
    progress, created = Progress.objects.get_or_create(
        user=user,
        lesson=lesson,
        defaults={'completed': True, 'completed_at': timezone.now()}
    )

    if not created and not progress.completed:
        progress.completed = True
        progress.completed_at = timezone.now()
        progress.save()

    return progress


def mark_lesson_incomplete(user: User, lesson: Lesson) -> None:
    """Mark a lesson as incomplete for user"""
    Progress.objects.filter(user=user, lesson=lesson).update(
        completed=False,
        completed_at=None
    )


def is_lesson_completed(user: User, lesson: Lesson) -> bool:
    """Check if user has completed this lesson"""
    return Progress.objects.filter(
        user=user,
        lesson=lesson,
        completed=True
    ).exists()


def get_course_progress(user: User, course: Course) -> Dict[str, Any]:
    """Calculate overall course progress for user"""
    total_lessons = Lesson.objects.filter(subsection__section__course=course).count()

    if total_lessons == 0:
        return {
            'total_lessons': 0,
            'completed_lessons': 0,
            'progress_percent': 0,
            'is_completed': False
        }

    completed_lessons = Progress.objects.filter(
        user=user,
        lesson__subsection__section__course=course,
        completed=True
    ).count()

    progress_percent = round((completed_lessons / total_lessons) * 100, 2)
    is_completed = progress_percent == 100

    if is_completed:
        enrollment = Enrollment.objects.filter(user=user, course=course).first()
        if enrollment and not enrollment.is_completed:
            enrollment.is_completed = True
            enrollment.save()

    return {
        'total_lessons': total_lessons,
        'completed_lessons': completed_lessons,
        'progress_percent': progress_percent,
        'is_completed': is_completed
    }

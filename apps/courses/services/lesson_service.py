"""
Lesson Service - Business logic for Lesson operations

This layer contains all business logic for Lesson management,
separated from views for better testability and reusability.
"""
from typing import Optional, List, Dict, Any
from django.contrib.auth.models import User
from django.db.models import QuerySet

from ..models import Lesson, Subsection, Course


def get_lesson_by_id(lesson_id: int) -> Optional[Lesson]:
    """Get lesson by ID"""
    return Lesson.objects.filter(id=lesson_id).select_related('subsection', 'subsection__section', 'subsection__section__course').first()


def get_lesson_for_instructor(lesson_id: int, instructor: User) -> Optional[Lesson]:
    """Get lesson only if user is course instructor"""
    return Lesson.objects.filter(
        id=lesson_id,
        subsection__section__course__instructor=instructor
    ).select_related('subsection', 'subsection__section', 'subsection__section__course').first()


def get_lessons_for_subsection(subsection: Subsection) -> QuerySet[Lesson]:
    """Get all lessons in a subsection ordered by position"""
    return Lesson.objects.filter(subsection=subsection).order_by('order')


def get_lessons_for_course(course: Course) -> QuerySet[Lesson]:
    """Get all lessons in a course"""
    return Lesson.objects.filter(subsection__section__course=course).order_by('subsection__section__order', 'subsection__order', 'order')


def create_lesson(data: Dict[str, Any], subsection: Subsection) -> Lesson:
    """Create a new lesson in a subsection"""
    lesson = Lesson(**data)
    lesson.subsection = subsection
    lesson.full_clean()
    lesson.save()
    return lesson


def update_lesson(lesson: Lesson, data: Dict[str, Any]) -> Lesson:
    """Update existing lesson"""
    for key, value in data.items():
        if hasattr(lesson, key):
            setattr(lesson, key, value)
    lesson.full_clean()
    lesson.save()
    return lesson


def delete_lesson(lesson: Lesson) -> None:
    """Delete lesson"""
    lesson.delete()


def reorder_lessons(subsection: Subsection, lesson_order: List[int]) -> None:
    """Reorder lessons in a subsection"""
    for index, lesson_id in enumerate(lesson_order):
        Lesson.objects.filter(id=lesson_id, subsection=subsection).update(order=index)


def get_next_lesson(lesson: Lesson) -> Optional[Lesson]:
    """Get next lesson in the same subsection"""
    return Lesson.objects.filter(
        subsection=lesson.subsection,
        order__gt=lesson.order
    ).order_by('order').first()


def get_previous_lesson(lesson: Lesson) -> Optional[Lesson]:
    """Get previous lesson in the same subsection"""
    return Lesson.objects.filter(
        subsection=lesson.subsection,
        order__lt=lesson.order
    ).order_by('-order').first()

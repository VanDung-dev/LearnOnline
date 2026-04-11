"""
Course Service - Business logic for Course operations

This layer contains all business logic for Course management,
separated from views for better testability and reusability.
"""
from typing import Optional, List, Dict, Any
from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.core.exceptions import ValidationError

from ..models import Course, Category, Enrollment


def get_course_by_slug(slug: str) -> Optional[Course]:
    """Get course by slug"""
    return Course.objects.filter(slug=slug).first()


def get_course_for_instructor(slug: str, instructor: User) -> Optional[Course]:
    """Get course only if user is instructor"""
    return Course.objects.filter(slug=slug, instructor=instructor).first()


def get_all_active_courses() -> QuerySet[Course]:
    """Get all active published courses"""
    return Course.objects.filter(is_active=True).select_related('category', 'instructor')


def get_courses_by_category(category_id: int) -> QuerySet[Course]:
    """Get courses for a specific category"""
    return Course.objects.filter(category_id=category_id, is_active=True)


def get_instructor_courses(instructor: User) -> QuerySet[Course]:
    """Get all courses created by instructor"""
    return Course.objects.filter(instructor=instructor)


def create_course(data: Dict[str, Any], instructor: User) -> Course:
    """Create a new course with business rules applied"""
    course = Course(**data)
    course.instructor = instructor
    course.full_clean()
    course.save()
    return course


def update_course(course: Course, data: Dict[str, Any]) -> Course:
    """Update existing course"""
    for key, value in data.items():
        if hasattr(course, key):
            setattr(course, key, value)
    course.full_clean()
    course.save()
    return course


def delete_course(course: Course) -> None:
    """Delete course with validation"""
    if Enrollment.objects.filter(course=course).exists():
        raise ValidationError("Cannot delete course with existing enrollments")
    course.delete()


def toggle_course_active(course: Course) -> Course:
    """Toggle course active status"""
    course.is_active = not course.is_active
    course.save()
    return course


def get_course_stats(course: Course) -> Dict[str, Any]:
    """Get statistics for a course"""
    return {
        'total_enrollments': Enrollment.objects.filter(course=course).count(),
        'completed_enrollments': Enrollment.objects.filter(course=course, is_completed=True).count(),
        'total_lessons': course.sections.prefetch_related('subsections__lessons').count(),
    }

"""
Services package for Courses application

Exports all service functions for easy import in views and other modules
"""
from .course_service import (
    get_course_by_slug,
    get_course_for_instructor,
    get_all_active_courses,
    get_courses_by_category,
    get_instructor_courses,
    create_course,
    update_course,
    delete_course,
    toggle_course_active,
    get_course_stats,
)

from .lesson_service import (
    get_lesson_by_id,
    get_lesson_for_instructor,
    get_lessons_for_subsection,
    get_lessons_for_course,
    create_lesson,
    update_lesson,
    delete_lesson,
    reorder_lessons,
    get_next_lesson,
    get_previous_lesson,
)

from .progress_service import (
    get_user_lesson_progress,
    mark_lesson_completed,
    mark_lesson_incomplete,
    is_lesson_completed,
    get_course_progress,
)

from .certificate_service import (
    can_generate_certificate,
    generate_certificate,
    get_certificate,
    get_user_certificates,
)

from .quiz_service import (
    grade_quiz_attempt,
    create_quiz_attempt,
    save_user_answers,
    get_quiz_results,
)

from .search_service import (
    get_popular_search_terms,
)


__all__ = [
    # Course Service
    'get_course_by_slug',
    'get_course_for_instructor',
    'get_all_active_courses',
    'get_courses_by_category',
    'get_instructor_courses',
    'create_course',
    'update_course',
    'delete_course',
    'toggle_course_active',
    'get_course_stats',

    # Lesson Service
    'get_lesson_by_id',
    'get_lesson_for_instructor',
    'get_lessons_for_subsection',
    'get_lessons_for_course',
    'create_lesson',
    'update_lesson',
    'delete_lesson',
    'reorder_lessons',
    'get_next_lesson',
    'get_previous_lesson',

    # Progress Service
    'get_user_lesson_progress',
    'mark_lesson_completed',
    'mark_lesson_incomplete',
    'is_lesson_completed',
    'get_course_progress',

    # Certificate Service
    'can_generate_certificate',
    'generate_certificate',
    'get_certificate',
    'get_user_certificates',

    # Quiz Service
    'grade_quiz_attempt',
    'create_quiz_attempt',
    'save_user_answers',
    'get_quiz_results',

    # Search Service
    'get_popular_search_terms',
]

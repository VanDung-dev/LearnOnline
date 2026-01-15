"""
Main views module that imports from separated view files
"""
# Import functions from separated view files
from .includes.views_course import (
    create_course, edit_course, delete_course, course_list,
    course_detail, course_learning_process, create_category_ajax,
    check_course_title
)
from .includes.views_section import (
    create_section, edit_section, delete_section
)
from .includes.views_subsection import (
    create_subsection, edit_subsection, delete_subsection
)
from .includes.views_lesson import (
    create_lesson, edit_lesson, delete_lesson
)
from .includes.views_lesson_detail import (
    lesson_detail, check_and_issue_certificate
)
from .includes.views_other import (
    home, enroll_course, support,
    instructor_courses, student_dashboard, delete_lesson_video, upload_image
)
from .includes.views_error import (
    custom_page_not_found, custom_server_error,
    custom_permission_denied, custom_bad_request,
    custom_method_not_allowed, custom_request_timeout,
    custom_too_many_requests, custom_bad_gateway,
    custom_service_unavailable, custom_gateway_timeout
)
from .includes.views_certificate import (
    public_certificate, purchase_certificate, course_certificate
)
from .includes.views_reorder import (
    reorder_sections,
    reorder_lessons,
    reorder_quiz_questions,
    reorder_subsections,
    reorder_subsection_lessons
)
from .includes.views_search import (
    search_autocomplete
)

__all__ = [
    'create_course', 'edit_course', 'delete_course', 'course_list',
    'course_detail', 'enroll_course', 'instructor_courses', 'student_dashboard',
    'create_section', 'edit_section', 'delete_section', 'reorder_sections',
    'create_subsection', 'edit_subsection', 'delete_subsection', 'reorder_subsections',
    'create_lesson', 'edit_lesson', 'delete_lesson', 'delete_lesson_video',
    'reorder_lessons', 'reorder_quiz_questions',
    'lesson_detail', 'check_and_issue_certificate',
    'public_certificate', 'purchase_certificate', 'home',
    'course_certificate', 'custom_page_not_found', 'upload_image',
    'course_learning_process', 'create_category_ajax', 'check_course_title',
    'custom_server_error', 'custom_permission_denied', 'custom_bad_request',
    'custom_method_not_allowed', 'custom_request_timeout',
    'custom_too_many_requests', 'custom_bad_gateway',
    'custom_service_unavailable', 'custom_gateway_timeout',
    'support', 'search_autocomplete'
]
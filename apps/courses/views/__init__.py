"""
Views package for the courses app.
Contains all view functions organized by feature.
"""
# Import all views from submodules for easy access
from .course_views import (
    create_course, edit_course, delete_course, course_list,
    course_detail, course_learning_process, create_category_ajax,
    check_course_title
)
from .section_views import (
    create_section, edit_section, delete_section
)
from .subsection_views import (
    create_subsection, edit_subsection, delete_subsection
)
from .lesson_views import (
    create_lesson, edit_lesson, delete_lesson
)
from .lesson_detail_views import (
    lesson_detail, check_and_issue_certificate
)
from .other_views import (
    home, enroll_course, support,
    instructor_courses, student_dashboard, delete_lesson_video, upload_image
)
from .error_handlers import (
    custom_page_not_found, custom_server_error,
    custom_permission_denied, custom_bad_request,
    custom_method_not_allowed, custom_request_timeout,
    custom_too_many_requests, custom_bad_gateway,
    custom_service_unavailable, custom_gateway_timeout
)
from .certificate_views import (
    public_certificate, purchase_certificate, course_certificate
)
from .reorder_views import (
    reorder_sections,
    reorder_lessons,
    reorder_quiz_questions,
    reorder_subsections,
    reorder_subsection_lessons
)
from .search_views import (
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

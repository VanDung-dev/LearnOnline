"""
Main views module that imports from separated view files
"""
# Import functions from separated view files
from .includes.views_course import (
    create_course, edit_course, delete_course, course_list, 
    course_detail, course_learning_process
)
from .includes.views_module import (
    create_module, edit_module, delete_module, reorder_modules
)
from .includes.views_lesson import (
    create_lesson, edit_lesson, delete_lesson, reorder_lessons
)
from .includes.views_lesson_detail import (
    lesson_detail, check_and_issue_certificate
)
from .includes.views_other import (
    home, custom_page_not_found, enroll_course,
    instructor_courses, delete_lesson_video, upload_image
)
from .includes.views_certificate import (
    public_certificate, purchase_certificate, course_certificate
)

__all__ = [
    'create_course', 'edit_course', 'delete_course', 'course_list',
    'course_detail', 'enroll_course', 'instructor_courses',
    'create_module', 'edit_module', 'delete_module', 'reorder_modules',
    'create_lesson', 'edit_lesson', 'delete_lesson', 'delete_lesson_video',
    'reorder_lessons', 'lesson_detail', 'check_and_issue_certificate',
    'public_certificate', 'purchase_certificate', 'home',
    'course_certificate', 'custom_page_not_found', 'upload_image',
    'course_learning_process'
]
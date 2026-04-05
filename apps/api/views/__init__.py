"""
API Views package for the api app.
Contains all API view classes organized by feature.
"""
# Import all views from submodules for easy access
from .auth_views import (
    RegisterView, ProfileView, ChangePasswordView
)
from .course_views import (
    CategoryViewSet, CourseViewSet, SectionViewSet, LessonDetailView
)
from .enrollment_views import (
    EnrollmentListView, ProgressViewSet, QuizDetailView, QuizSubmitView,
    CertificateListView
)
from .discussion_views import (
    IsEnrolledOrInstructor, DiscussionViewSet, ReplyViewSet
)
from .admin_views import (
    _SchoolScopedMixin,
    InstructorInviteCreateView, InstructorInviteAcceptView, StudentJoinSchoolView,
    SchoolAdminCoursesView, SchoolAdminEnrollmentsView, SchoolAdminCertificatesView,
    SchoolAdminInstructorsView, SchoolAdminStudentsView
)

__all__ = [
    # Auth
    'RegisterView', 'ProfileView', 'ChangePasswordView',
    # Course
    'CategoryViewSet', 'CourseViewSet', 'SectionViewSet', 'LessonDetailView',
    # Enrollment/Progress
    'EnrollmentListView', 'ProgressViewSet', 'QuizDetailView', 'QuizSubmitView',
    'CertificateListView',
    # Discussion
    'IsEnrolledOrInstructor', 'DiscussionViewSet', 'ReplyViewSet',
    # Admin
    '_SchoolScopedMixin',
    'InstructorInviteCreateView', 'InstructorInviteAcceptView', 'StudentJoinSchoolView',
    'SchoolAdminCoursesView', 'SchoolAdminEnrollmentsView', 'SchoolAdminCertificatesView',
    'SchoolAdminInstructorsView', 'SchoolAdminStudentsView',
]

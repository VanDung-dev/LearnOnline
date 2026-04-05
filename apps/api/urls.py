"""
API URL Configuration for LearnOnline.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from .views import (
    # Auth
    RegisterView, ProfileView, ChangePasswordView,
    # Course
    CategoryViewSet, CourseViewSet, SectionViewSet, LessonDetailView,
    # Enrollment/Progress
    EnrollmentListView, ProgressViewSet, QuizDetailView, QuizSubmitView, CertificateListView,
    # Discussion
    DiscussionViewSet, ReplyViewSet,
    # Admin
    InstructorInviteCreateView, InstructorInviteAcceptView, StudentJoinSchoolView,
    SchoolAdminCoursesView, SchoolAdminEnrollmentsView, SchoolAdminCertificatesView,
    SchoolAdminInstructorsView, SchoolAdminStudentsView
)
from . import search_views

# Create a router for viewsets
router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'progress', ProgressViewSet, basename='progress')
router.register(r'discussions', DiscussionViewSet, basename='discussion')
router.register(r'replies', ReplyViewSet, basename='reply')

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),

    # ============================================
    # Authentication URLs
    # ============================================
    path('auth/register/', RegisterView.as_view(), name='api-register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='api-token-obtain'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='api-token-refresh'),
    path('auth/profile/', ProfileView.as_view(), name='api-profile'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='api-change-password'),

    # ============================================
    # Organization / Instructor Invite URLs
    # ============================================
    path('schools/<int:school_id>/instructor-invites/', InstructorInviteCreateView.as_view(), name='api-instructor-invite-create'),
    path('instructor-invites/accept/', InstructorInviteAcceptView.as_view(), name='api-instructor-invite-accept'),
    path('schools/<int:school_id>/join/', StudentJoinSchoolView.as_view(), name='api-student-join-school'),

    # ============================================
    # School Admin (Tenant-filtered) URLs
    # ============================================
    path('schools/<int:school_id>/admin/courses/', SchoolAdminCoursesView.as_view(), name='api-admin-courses'),
    path('schools/<int:school_id>/admin/enrollments/', SchoolAdminEnrollmentsView.as_view(), name='api-admin-enrollments'),
    path('schools/<int:school_id>/admin/certificates/', SchoolAdminCertificatesView.as_view(), name='api-admin-certificates'),
    path('schools/<int:school_id>/admin/instructors/', SchoolAdminInstructorsView.as_view(), name='api-admin-instructors'),
    path('schools/<int:school_id>/admin/students/', SchoolAdminStudentsView.as_view(), name='api-admin-students'),

    # ============================================
    # Nested Course URLs
    # ============================================
    path(
        'courses/<slug:course_slug>/sections/',
        SectionViewSet.as_view({'get': 'list'}),
        name='course-sections'
    ),
    path(
        'courses/<slug:course_slug>/sections/<int:pk>/',
        SectionViewSet.as_view({'get': 'retrieve'}),
        name='course-section-detail'
    ),

    # ============================================
    # Lesson URLs
    # ============================================
    path('lessons/<int:pk>/', LessonDetailView.as_view(), name='lesson-detail'),

    # ============================================
    # Enrollment URLs
    # ============================================
    path('enrollments/', EnrollmentListView.as_view(), name='enrollment-list'),

    # ============================================
    # Quiz URLs
    # ============================================
    path('quizzes/<int:lesson_id>/', QuizDetailView.as_view(), name='quiz-detail'),
    path('quizzes/<int:lesson_id>/submit/', QuizSubmitView.as_view(), name='quiz-submit'),

    # ============================================
    # Certificate URLs
    # ============================================
    path('certificates/', CertificateListView.as_view(), name='certificate-list'),

    # ============================================
    # Search URLs
    # ============================================
    path('search/courses/', search_views.SearchCoursesView.as_view(), name='search-courses'),
    path('search/lessons/', search_views.SearchLessonsView.as_view(), name='search-lessons'),
    path('search/', search_views.SearchGlobalView.as_view(), name='search-global'),
    path('search/popular/', search_views.PopularSearchTermsView.as_view(), name='search-popular'),
    path('search/autocomplete/', search_views.AutocompleteView.as_view(), name='search-autocomplete'),

    # ============================================
    # API Documentation (OpenAPI/Swagger)
    # ============================================
    path('schema/', SpectacularAPIView.as_view(), name='api-schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='api-schema'), name='api-docs'),
    path('redoc/', SpectacularRedocView.as_view(url_name='api-schema'), name='api-redoc'),
]

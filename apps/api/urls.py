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

from . import views
from . import search_views
from apps.discussions import api_views as discussion_views

# Create a router for viewsets
router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'courses', views.CourseViewSet, basename='course')
router.register(r'progress', views.ProgressViewSet, basename='progress')
router.register(r'discussions', discussion_views.DiscussionViewSet, basename='discussion')
router.register(r'replies', discussion_views.ReplyViewSet, basename='reply')

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),

    # ============================================
    # Authentication URLs
    # ============================================
    path('auth/register/', views.RegisterView.as_view(), name='api-register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='api-token-obtain'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='api-token-refresh'),
    path('auth/profile/', views.ProfileView.as_view(), name='api-profile'),
    path('auth/change-password/', views.ChangePasswordView.as_view(), name='api-change-password'),

    # ============================================
    # Organization / Instructor Invite URLs
    # ============================================
    path('schools/<int:school_id>/instructor-invites/', views.InstructorInviteCreateView.as_view(), name='api-instructor-invite-create'),
    path('instructor-invites/accept/', views.InstructorInviteAcceptView.as_view(), name='api-instructor-invite-accept'),
    path('schools/<int:school_id>/join/', views.StudentJoinSchoolView.as_view(), name='api-student-join-school'),

    # ============================================
    # School Admin (Tenant-filtered) URLs
    # ============================================
    path('schools/<int:school_id>/admin/courses/', views.SchoolAdminCoursesView.as_view(), name='api-admin-courses'),
    path('schools/<int:school_id>/admin/enrollments/', views.SchoolAdminEnrollmentsView.as_view(), name='api-admin-enrollments'),
    path('schools/<int:school_id>/admin/certificates/', views.SchoolAdminCertificatesView.as_view(), name='api-admin-certificates'),
    path('schools/<int:school_id>/admin/instructors/', views.SchoolAdminInstructorsView.as_view(), name='api-admin-instructors'),
    path('schools/<int:school_id>/admin/students/', views.SchoolAdminStudentsView.as_view(), name='api-admin-students'),

    # ============================================
    # Nested Course URLs
    # ============================================
    path(
        'courses/<slug:course_slug>/modules/',
        views.ModuleViewSet.as_view({'get': 'list'}),
        name='course-modules'
    ),
    path(
        'courses/<slug:course_slug>/modules/<int:pk>/',
        views.ModuleViewSet.as_view({'get': 'retrieve'}),
        name='course-module-detail'
    ),

    # ============================================
    # Lesson URLs
    # ============================================
    path('lessons/<int:pk>/', views.LessonDetailView.as_view(), name='lesson-detail'),

    # ============================================
    # Enrollment URLs
    # ============================================
    path('enrollments/', views.EnrollmentListView.as_view(), name='enrollment-list'),

    # ============================================
    # Quiz URLs
    # ============================================
    path('quizzes/<int:lesson_id>/', views.QuizDetailView.as_view(), name='quiz-detail'),
    path('quizzes/<int:lesson_id>/submit/', views.QuizSubmitView.as_view(), name='quiz-submit'),

    # ============================================
    # Certificate URLs
    # ============================================
    path('certificates/', views.CertificateListView.as_view(), name='certificate-list'),

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

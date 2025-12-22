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

# Create a router for viewsets
router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'courses', views.CourseViewSet, basename='course')
router.register(r'progress', views.ProgressViewSet, basename='progress')

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
    # API Documentation (OpenAPI/Swagger)
    # ============================================
    path('schema/', SpectacularAPIView.as_view(), name='api-schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='api-schema'), name='api-docs'),
    path('redoc/', SpectacularRedocView.as_view(url_name='api-schema'), name='api-redoc'),
]

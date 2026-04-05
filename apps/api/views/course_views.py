"""
Course API Views.
Contains views for categories, courses, sections, and lessons.
"""

from django.shortcuts import get_object_or_404
from rest_framework import viewsets, generics, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from apps.courses.models import Category, Course, Section, Lesson, Enrollment
from ..serializers import (
    CategorySerializer, CourseListSerializer, CourseDetailSerializer,
    SectionSerializer, LessonSerializer, EnrollmentSerializer
)
from ..permissions import IsEnrolled


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for categories (read-only).
    GET /api/categories/
    GET /api/categories/{id}/
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for courses (read-only for public, enrollable for authenticated).
    GET /api/courses/
    GET /api/courses/{slug}/
    POST /api/courses/{slug}/enroll/
    """
    queryset = Course.objects.select_related(
        'instructor', 'category'
    ).prefetch_related('sections__lessons')
    lookup_field = 'slug'
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__id=category)
        
        # Filter by price
        is_free = self.request.query_params.get('is_free')
        if is_free is not None:
            queryset = queryset.filter(is_free=is_free.lower() == 'true')
        
        # Search by title
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(title__icontains=search)
        
        return queryset

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def enroll(self, request, slug=None):
        """Enroll current user in this course."""
        course = self.get_object()
        user = request.user

        # Check if already enrolled
        if Enrollment.objects.filter(user=user, course=course).exists():
            return Response(
                {"error": "You are already enrolled in this course."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if course is free
        if not course.is_free:
            return Response(
                {"error": "This course requires payment. Please use the payment API."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create enrollment
        enrollment = Enrollment.objects.create(user=user, course=course)
        serializer = EnrollmentSerializer(enrollment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SectionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for sections (formerly modules).
    GET /api/courses/{course_slug}/sections/
    GET /api/courses/{course_slug}/sections/{id}/
    """
    serializer_class = SectionSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        course_slug = self.kwargs.get('course_slug')
        return Section.objects.filter(course__slug=course_slug).prefetch_related('lessons')


class LessonDetailView(generics.RetrieveAPIView):
    """
    Get lesson detail (requires enrollment for full content).
    GET /api/lessons/{id}/
    """
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, IsEnrolled]

    def get_queryset(self):
        return Lesson.objects.select_related('section__course')

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, obj)
        return obj

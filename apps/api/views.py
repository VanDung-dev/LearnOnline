"""
API Views and ViewSets for LearnOnline
RESTful endpoints for courses, enrollments, progress, authentication.
"""

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, generics, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.accounts.models import Profile
from apps.courses.models import (
    Category, Course, Module, Lesson, Quiz,
    Enrollment, Progress, Certificate, QuizAttempt
)
from .serializers import (
    UserSerializer, ProfileSerializer, RegisterSerializer, ChangePasswordSerializer,
    CategorySerializer, CourseListSerializer, CourseDetailSerializer,
    ModuleSerializer, LessonSerializer, QuizSerializer,
    EnrollmentSerializer, ProgressSerializer, CertificateSerializer,
    QuizSubmitSerializer, QuizAttemptSerializer
)
from .permissions import IsOwnerOrReadOnly, IsInstructor, IsEnrolled


# ============================================
# Authentication Views
# ============================================

class RegisterView(generics.CreateAPIView):
    """
    User registration endpoint.
    POST /api/auth/register/
    """
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    Get or update current user's profile.
    GET/PUT /api/auth/profile/
    """
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.profile


class ChangePasswordView(generics.UpdateAPIView):
    """
    Change password for current user.
    PUT /api/auth/change-password/
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Check old password
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {"old_password": "Wrong password."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Set new password
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({"message": "Password updated successfully."})


# ============================================
# Category Views
# ============================================

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for categories (read-only).
    GET /api/categories/
    GET /api/categories/{id}/
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


# ============================================
# Course Views
# ============================================

class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for courses (read-only for public, enrollable for authenticated).
    GET /api/courses/
    GET /api/courses/{slug}/
    POST /api/courses/{slug}/enroll/
    """
    queryset = Course.objects.select_related(
        'instructor', 'category'
    ).prefetch_related('modules__lessons')
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


# ============================================
# Module & Lesson Views
# ============================================

class ModuleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for modules.
    GET /api/courses/{course_slug}/modules/
    GET /api/courses/{course_slug}/modules/{id}/
    """
    serializer_class = ModuleSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        course_slug = self.kwargs.get('course_slug')
        return Module.objects.filter(course__slug=course_slug).prefetch_related('lessons')


class LessonDetailView(generics.RetrieveAPIView):
    """
    Get lesson detail (requires enrollment for full content).
    GET /api/lessons/{id}/
    """
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, IsEnrolled]

    def get_queryset(self):
        return Lesson.objects.select_related('module__course')

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, obj)
        return obj


# ============================================
# Enrollment & Progress Views
# ============================================

class EnrollmentListView(generics.ListAPIView):
    """
    List current user's enrollments.
    GET /api/enrollments/
    """
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Enrollment.objects.filter(
            user=self.request.user
        ).select_related('course__instructor', 'course__category')


class ProgressViewSet(viewsets.ModelViewSet):
    """
    ViewSet for tracking progress.
    GET /api/progress/
    POST /api/progress/
    PUT /api/progress/{id}/
    """
    serializer_class = ProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Progress.objects.filter(
            user=self.request.user
        ).select_related('lesson__module__course')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def complete_lesson(self, request):
        """Mark a lesson as completed."""
        lesson_id = request.data.get('lesson_id')
        if not lesson_id:
            return Response(
                {"error": "lesson_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        lesson = get_object_or_404(Lesson, pk=lesson_id)
        
        # Check enrollment
        if not Enrollment.objects.filter(
            user=request.user, course=lesson.module.course
        ).exists():
            return Response(
                {"error": "You are not enrolled in this course."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Create or update progress
        progress, created = Progress.objects.update_or_create(
            user=request.user,
            lesson=lesson,
            defaults={'completed': True}
        )
        
        serializer = ProgressSerializer(progress)
        return Response(serializer.data)


# ============================================
# Quiz Views
# ============================================

class QuizDetailView(generics.RetrieveAPIView):
    """
    Get quiz details (requires enrollment).
    GET /api/quizzes/{lesson_id}/
    """
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        lesson_id = self.kwargs.get('lesson_id')
        lesson = get_object_or_404(Lesson, pk=lesson_id, lesson_type='quiz')
        
        # Check enrollment
        if not Enrollment.objects.filter(
            user=self.request.user, course=lesson.module.course
        ).exists():
            self.permission_denied(self.request, message="Not enrolled in this course.")
        
        return lesson.quiz


class QuizSubmitView(APIView):
    """
    Submit quiz answers.
    POST /api/quizzes/{lesson_id}/submit/
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, pk=lesson_id, lesson_type='quiz')
        
        # Check enrollment
        if not Enrollment.objects.filter(
            user=request.user, course=lesson.module.course
        ).exists():
            return Response(
                {"error": "Not enrolled in this course."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = QuizSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Calculate score
        quiz = lesson.quiz
        total_points = 0
        earned_points = 0
        
        for question in quiz.questions.all():
            total_points += question.points
            submitted_answers = serializer.validated_data['answers'].get(str(question.id), [])
            correct_answers = set(question.answers.filter(is_correct=True).values_list('id', flat=True))
            
            if set(submitted_answers) == correct_answers:
                earned_points += question.points

        score = (earned_points / total_points * 100) if total_points > 0 else 0

        # Create attempt record
        attempt_number = QuizAttempt.objects.filter(
            user=request.user, lesson=lesson
        ).count() + 1

        attempt = QuizAttempt.objects.create(
            user=request.user,
            lesson=lesson,
            attempt_number=attempt_number,
            score=score
        )

        return Response({
            "score": score,
            "earned_points": earned_points,
            "total_points": total_points,
            "attempt_number": attempt_number
        })


# ============================================
# Certificate Views
# ============================================

class CertificateListView(generics.ListAPIView):
    """
    List current user's certificates.
    GET /api/certificates/
    """
    serializer_class = CertificateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Certificate.objects.filter(
            user=self.request.user
        ).select_related('course')

"""
Enrollment, Progress, Quiz, and Certificate API Views.
"""

from django.shortcuts import get_object_or_404
from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.courses.models import (
    Lesson, Quiz, Enrollment, Progress, Certificate, QuizAttempt
)
from ..serializers import (
    EnrollmentSerializer, ProgressSerializer, QuizSerializer,
    QuizSubmitSerializer, QuizAttemptSerializer, CertificateSerializer
)


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
        ).select_related('lesson__section__course')

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
            user=request.user, course=lesson.section.course
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
            user=self.request.user, course=lesson.section.course
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
            user=request.user, course=lesson.section.course
        ).exists():
            return Response(
                {"error": "Not enrolled in this course."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check max_check limit (0 means unlimited)
        current_attempts = QuizAttempt.objects.filter(
            user=request.user, lesson=lesson
        ).count()
        
        if lesson.max_check > 0 and current_attempts >= lesson.max_check:
            return Response(
                {"error": f"Maximum number of attempts ({lesson.max_check}) reached for this quiz."},
                status=status.HTTP_400_BAD_REQUEST
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

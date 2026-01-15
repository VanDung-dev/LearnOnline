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
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.accounts.models import Profile
from apps.courses.models import (
    Category, Course, Section, Lesson, Quiz,
    Enrollment, Progress, Certificate, QuizAttempt
)
from .serializers import (
    UserSerializer, ProfileSerializer, RegisterSerializer, ChangePasswordSerializer,
    CategorySerializer, CourseListSerializer, CourseDetailSerializer,
    SectionSerializer, LessonSerializer, QuizSerializer,
    EnrollmentSerializer, ProgressSerializer, CertificateSerializer,
    QuizSubmitSerializer, QuizAttemptSerializer,
    InstructorInviteSerializer
)
from .permissions import IsOwnerOrReadOnly, IsInstructor, IsEnrolled, IsSchoolAdmin
from apps.organization.models import School, InstructorInvite
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models import Q


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
# Organization / Instructor Invite Views
# ============================================


class InstructorInviteCreateView(generics.CreateAPIView):
    """
    Create an instructor invitation for a given school.
    POST /api/schools/{school_id}/instructor-invites/
    Body: {"email": "john@example.com"}
    """
    serializer_class = InstructorInviteSerializer
    permission_classes = [permissions.IsAuthenticated, IsSchoolAdmin]

    def create(self, request, *args, **kwargs):
        school_id = self.kwargs.get('school_id')
        email = request.data.get('email')
        if not email:
            return Response({"email": "This field is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure current school admin only invites for their own school
        current_school = getattr(request.user.profile, 'school', None)
        if not current_school or str(current_school.id) != str(school_id):
            return Response({"detail": "You can only invite for your own school."}, status=status.HTTP_403_FORBIDDEN)

        token = InstructorInvite.generate_token()
        invite = InstructorInvite.objects.create(
            email=email,
            school=current_school,
            token=token,
            invited_by=request.user
        )

        serializer = self.get_serializer(invite)
        # Build activation URL for client to send via email later
        activation_url = request.build_absolute_uri(
            reverse('api-instructor-invite-accept')
        ) + f"?token={token}"
        data = serializer.data
        data["activation_url"] = activation_url
        return Response(data, status=status.HTTP_201_CREATED)


class InstructorInviteAcceptView(APIView):
    """
    Accept an instructor invitation.
    POST /api/instructor-invites/accept/
    Body: {"token": "...", "password": "...", "first_name": "...", "last_name": "..."}
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = request.data.get('token') or request.GET.get('token')
        password = request.data.get('password')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')

        if not token:
            return Response({"token": "This field is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not password:
            return Response({"password": "This field is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            invite = InstructorInvite.objects.get(token=token, status=InstructorInvite.PENDING)
        except InstructorInvite.DoesNotExist:
            return Response({"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        # Create or update user
        email = invite.email
        username_base = email.split('@')[0]
        username = username_base
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{username_base}{counter}"
            counter += 1

        user, created = User.objects.get_or_create(email=email, defaults={
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
        })
        user.set_password(password)
        user.save()

        # Ensure profile exists and set role/school
        profile = getattr(user, 'profile', None)
        if not profile:
            profile = Profile.objects.create(user=user)
        profile.role = Profile.INSTRUCTOR
        profile.school = invite.school
        profile.save()

        invite.mark_accepted()

        return Response({"message": "Invitation accepted. Account activated.", "user_id": user.id})


class StudentJoinSchoolView(APIView):
    """
    Allow a student to join a school by verifying email domain matches school's domain.
    POST /api/schools/{school_id}/join/
    Body: {"email": "student@hcmus.edu.vn"}
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, school_id):
        email = request.data.get('email')
        if not email:
            return Response({"email": "This field is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            school = School.objects.get(pk=school_id)
        except School.DoesNotExist:
            return Response({"detail": "School not found."}, status=status.HTTP_404_NOT_FOUND)

        # Verify email domain matches the school's domain
        if '@' not in email:
            return Response({"email": "Invalid email."}, status=status.HTTP_400_BAD_REQUEST)
        domain = email.split('@')[-1].lower().strip()
        if domain != school.domain.lower():
            return Response({"detail": "Email domain does not match the school's domain."}, status=status.HTTP_400_BAD_REQUEST)

        # Assign school to current user's profile
        profile = request.user.profile
        profile.school = school
        # Keep role as-is (student by default)
        profile.save(update_fields=["school"])

        return Response({"message": "Joined school successfully.", "school_id": school.id, "school_name": school.name})


# ============================================
# School Admin Views (Tenant-filtered)
# ============================================

class _SchoolScopedMixin:
    """Helper mixin to validate and obtain current school from URL kwarg."""

    def _get_and_validate_school(self, request, school_id):
        current_school = getattr(getattr(request.user, 'profile', None), 'school', None)
        if not current_school or str(current_school.id) != str(school_id):
            raise PermissionDenied("You can only access resources of your own school.")
        return current_school


class SchoolAdminCoursesView(_SchoolScopedMixin, generics.ListAPIView):
    """
    List courses that belong to the current school (by instructor's school).
    GET /api/schools/{school_id}/admin/courses/
    """
    serializer_class = CourseListSerializer
    permission_classes = [permissions.IsAuthenticated, IsSchoolAdmin]

    def get_queryset(self):
        school_id = self.kwargs.get('school_id')
        school = self._get_and_validate_school(self.request, school_id)
        return Course.objects.select_related('instructor', 'category') \
            .filter(instructor__profile__school=school)


class SchoolAdminEnrollmentsView(_SchoolScopedMixin, generics.ListAPIView):
    """
    List enrollments for courses under the current school.
    GET /api/schools/{school_id}/admin/enrollments/
    """
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsSchoolAdmin]

    def get_queryset(self):
        school_id = self.kwargs.get('school_id')
        school = self._get_and_validate_school(self.request, school_id)
        return Enrollment.objects.select_related('course__instructor', 'course__category', 'user') \
            .filter(course__instructor__profile__school=school)


class SchoolAdminCertificatesView(_SchoolScopedMixin, generics.ListAPIView):
    """
    List certificates issued for courses under the current school.
    GET /api/schools/{school_id}/admin/certificates/
    """
    serializer_class = CertificateSerializer
    permission_classes = [permissions.IsAuthenticated, IsSchoolAdmin]

    def get_queryset(self):
        school_id = self.kwargs.get('school_id')
        school = self._get_and_validate_school(self.request, school_id)
        return Certificate.objects.select_related('course', 'user', 'enrollment') \
            .filter(course__instructor__profile__school=school)


class SchoolAdminInstructorsView(_SchoolScopedMixin, generics.ListAPIView):
    """
    List instructors of the current school.
    GET /api/schools/{school_id}/admin/instructors/
    """
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsSchoolAdmin]

    def get_queryset(self):
        school_id = self.kwargs.get('school_id')
        school = self._get_and_validate_school(self.request, school_id)
        return Profile.objects.select_related('user', 'school') \
            .filter(role=Profile.INSTRUCTOR, school=school)


class SchoolAdminStudentsView(_SchoolScopedMixin, generics.ListAPIView):
    """
    List students associated with the current school.
    Includes students whose profile.school matches OR who are enrolled in the school's courses.
    GET /api/schools/{school_id}/admin/students/
    """
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsSchoolAdmin]

    def get_queryset(self):
        school_id = self.kwargs.get('school_id')
        school = self._get_and_validate_school(self.request, school_id)
        return Profile.objects.select_related('user', 'school') \
            .filter(role=Profile.STUDENT) \
            .filter(Q(school=school) | Q(user__enrollments__course__instructor__profile__school=school)) \
            .distinct()


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


# ============================================
# Module & Lesson Views
# ============================================

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

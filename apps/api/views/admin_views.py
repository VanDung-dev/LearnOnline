"""
Organization and School Admin API Views.
Contains views for instructor invites, school admin endpoints, and student join.
"""

from django.contrib.auth.models import User
from django.db.models import Q
from django.urls import reverse
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from apps.accounts.models import Profile
from apps.courses.models import Course, Enrollment, Certificate
from apps.organization.models import School, InstructorInvite
from ..serializers import (
    ProfileSerializer, CourseListSerializer, EnrollmentSerializer,
    CertificateSerializer, InstructorInviteSerializer
)
from ..permissions import IsSchoolAdmin


class _SchoolScopedMixin:
    """Helper mixin to validate and obtain current school from URL kwarg."""

    def _get_and_validate_school(self, request, school_id):
        current_school = getattr(getattr(request.user, 'profile', None), 'school', None)
        if not current_school or str(current_school.id) != str(school_id):
            raise PermissionDenied("You can only access resources of your own school.")
        return current_school


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


class InstructorInviteAcceptView(generics.GenericAPIView):
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


class StudentJoinSchoolView(generics.GenericAPIView):
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

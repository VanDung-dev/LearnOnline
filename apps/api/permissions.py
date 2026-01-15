"""
Custom permissions for the API.
"""

from rest_framework import permissions

from apps.courses.models import Enrollment


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner
        return obj.user == request.user


class IsInstructor(permissions.BasePermission):
    """
    Permission to check if user is an instructor.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return hasattr(request.user, 'profile') and request.user.profile.is_instructor()


class IsEnrolled(permissions.BasePermission):
    """
    Permission to check if user is enrolled in the course.
    """
    message = "You must be enrolled in this course to access this content."

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Get the course from the object (lesson -> section -> course)
        if hasattr(obj, 'section'):
            course = obj.section.course
        elif hasattr(obj, 'course'):
            course = obj.course
        else:
            return False

        return Enrollment.objects.filter(
            user=request.user, course=course
        ).exists()


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit, others can read.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsSchoolAdmin(permissions.BasePermission):
    """
    Permission to allow only School Admins.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if not hasattr(user, 'profile'):
            return False
        return user.profile.is_school_admin()

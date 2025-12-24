from django.http import JsonResponse


class SchoolAccessControlMiddleware:
    """
    Middleware to enforce tenant isolation for school admins/instructors.

    If an authenticated user is associated with a school and attempts to access
    resources of another school via explicit `school_id` in query params or request data,
    respond with 403 Forbidden.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        if user and user.is_authenticated and hasattr(user, 'profile'):
            # Attach current school to request for convenience
            request.current_school = getattr(user.profile, 'school', None)

            # Only enforce for school-scoped roles
            if user.profile.is_school_admin() or user.profile.is_instructor():
                target_school_id = (
                    request.GET.get('school_id')
                    or (request.POST.get('school_id') if request.method in ('POST', 'PUT', 'PATCH', 'DELETE') else None)
                )
                if target_school_id and request.current_school:
                    try:
                        target_school_id_int = int(target_school_id)
                    except (TypeError, ValueError):
                        return JsonResponse({"detail": "Invalid school_id."}, status=400)

                    if target_school_id_int != request.current_school.id:
                        return JsonResponse({"detail": "Cross-tenant access is forbidden."}, status=403)

        response = self.get_response(request)
        return response

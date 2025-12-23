from django.shortcuts import redirect
from django.urls import reverse


class AdminAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the request path starts with /admin/
        if request.path.startswith('/admin/'):
            # Check if user is authenticated and is staff (admin)
            if not (request.user.is_authenticated and request.user.is_staff):
                # Redirect to home page if not admin
                return redirect('courses:home')
        
        response = self.get_response(request)
        return response
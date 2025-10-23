from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages


class AdminAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the request is for the admin interface
        if request.path.startswith('/admin/'):
            # Check if user is authenticated
            if not request.user.is_authenticated:
                messages.error(request, 'You need to be logged in to access the admin interface.')
                return redirect('accounts:login')
            
            # Check if user is a superuser or has a profile and is an admin
            if not request.user.is_superuser and (not hasattr(request.user, 'profile') or not request.user.profile.is_admin()):
                messages.error(request, 'You do not have permission to access the admin interface.')
                return redirect('courses:home')
        
        response = self.get_response(request)
        return response
from .models import Profile


class ProfileMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                request.user.profile
            except Profile.DoesNotExist:
                Profile.objects.create(user=request.user)
        
        response = self.get_response(request)
        return response
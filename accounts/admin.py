from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from .models import Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)

# Unregister the default User admin
admin.site.unregister(User)
# Register the User model with CustomUserAdmin
admin.site.register(User, CustomUserAdmin)

# Register the Profile model
admin.site.register(Profile)

# Override the logout behavior
def logout_view(request):
    # Perform the normal logout
    from django.contrib.auth import logout
    logout(request)
    
    # Redirect to home page
    return HttpResponseRedirect('/')

# Store the original logout method
original_logout = admin.site.logout

# Override the admin logout method
def custom_admin_logout(request, extra_context=None):
    # Check if user is admin before logout
    is_admin = (hasattr(request.user, 'is_superuser') and request.user.is_superuser) or (
            hasattr(request.user, 'profile') and getattr(request.user.profile, 'is_admin', lambda: False)())
    
    # Call the original logout
    response = original_logout(request, extra_context)
    
    # Redirect admin users to home page
    if is_admin:
        return HttpResponseRedirect('/')
    
    # Return the original response for non-admin users
    return response

# Apply the custom logout method
admin.site.logout = custom_admin_logout
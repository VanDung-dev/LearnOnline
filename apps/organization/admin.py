from django.contrib import admin, messages
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from apps.accounts.models import Profile
from .models import School


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "domain", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("name", "code", "domain")
    actions = ("create_school_admin",)

    @admin.action(description="Create School Admin for selected schools")
    def create_school_admin(self, request, queryset):
        created = 0
        skipped = 0
        details = []
        for school in queryset:
            username = f"admin_{school.code}"
            email = f"admin@{school.domain}"
            if User.objects.filter(username=username).exists():
                skipped += 1
                continue
            temp_password = get_random_string(12)
            user = User.objects.create_user(username=username, email=email, password=temp_password, is_staff=True)
            # Ensure profile exists and set role/school
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.role = Profile.SCHOOL_ADMIN
            profile.school = school
            profile.save()
            created += 1
            details.append(f"{username}/{email} (pwd: {temp_password}) for {school.code}")

        if created:
            messages.success(request, f"Created {created} School Admin(s):\n" + "\n".join(details))
        if skipped:
            messages.warning(request, f"Skipped {skipped} school(s) because admin user already exists.")

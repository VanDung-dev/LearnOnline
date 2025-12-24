from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from django.utils import timezone


class School(models.Model):
    ACTIVE = "active"
    INACTIVE = "inactive"
    STATUS_CHOICES = (
        (ACTIVE, "Active"),
        (INACTIVE, "Inactive"),
    )

    name = models.CharField(max_length=255)
    code = models.SlugField(max_length=50, unique=True)
    domain = models.CharField(max_length=255, unique=True, help_text="Email domain, e.g. hcmus.edu.vn")
    logo = models.ImageField(upload_to="school_logos/", null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "organization_school"
        verbose_name = "School"
        verbose_name_plural = "Schools"

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"


class InstructorInvite(models.Model):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REVOKED = "revoked"
    STATUS_CHOICES = (
        (PENDING, "Pending"),
        (ACCEPTED, "Accepted"),
        (REVOKED, "Revoked"),
    )

    email = models.EmailField()
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="invites")
    token = models.CharField(max_length=64, unique=True, db_index=True)
    invited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="instructor_invites_sent")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    accepted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "organization_instructor_invite"
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["token"]),
        ]

    def __str__(self):
        return f"Invite {self.email} -> {self.school.code} ({self.status})"

    @staticmethod
    def generate_token() -> str:
        return get_random_string(48)

    def mark_accepted(self):
        self.status = self.ACCEPTED
        self.accepted_at = timezone.now()
        self.save(update_fields=["status", "accepted_at"])

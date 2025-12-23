from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    TYPES = (
        ('system', 'System'),
        ('course', 'Course'),
        ('payment', 'Payment'),
        ('discussion', 'Discussion'),
    )
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True)
    notification_type = models.CharField(max_length=20, choices=TYPES, default='system')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.recipient.username}"

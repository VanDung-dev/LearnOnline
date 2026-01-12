from django.db import models
from django.contrib.auth.models import User
from apps.courses.models import Course, Enrollment


class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('visa', 'Visa'),
        ('mastercard', 'Mastercard'),
        ('paypal', 'PayPal'),
        ('momo', 'MoMo'),
        ('zalopay', 'ZaloPay'),
        ('local_bank', 'Local Bank (QR)'),
    ]
    
    PAYMENT_TYPE_CHOICES = [
        ('course', 'Course'),
        ('certificate', 'Certificate'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    purchase_type = models.CharField(max_length=15, choices=PAYMENT_TYPE_CHOICES, default='course')
    transaction_id = models.CharField(max_length=100, unique=True)
    processor_transaction_id = models.CharField(max_length=150, null=True, blank=True, db_index=True)
    idempotency_key = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.user.username} - {self.amount} {self.currency}"

    class Meta:
        indexes = [
            models.Index(fields=["user", "course", "purchase_type"]),
        ]


class PaymentLog(models.Model):
    """Audit trail for payment events."""
    EVENT_TYPES = [
        ('created', 'Payment Created'),
        ('status_change', 'Status Changed'),
        ('webhook_received', 'Webhook Received'),
        ('refund_initiated', 'Refund Initiated'),
    ]

    payment = models.ForeignKey(
        Payment, on_delete=models.CASCADE, related_name='logs'
    )
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)
    previous_status = models.CharField(max_length=20, null=True, blank=True)
    new_status = models.CharField(max_length=20, null=True, blank=True)
    message = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['payment', 'event_type']),
        ]

    def __str__(self):
        return f"{self.event_type} - {self.payment.transaction_id}"

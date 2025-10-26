from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'course', 'amount', 'currency', 'status', 'payment_method', 'created_at')
    list_filter = ('status', 'payment_method', 'currency', 'created_at')
    search_fields = ('transaction_id', 'user__username', 'course__title')
    readonly_fields = ('created_at', 'updated_at')
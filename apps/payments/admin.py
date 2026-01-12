from django.contrib import admin
from .models import Payment, PaymentLog


class PaymentLogInline(admin.TabularInline):
    model = PaymentLog
    readonly_fields = [
        'event_type', 'previous_status', 'new_status',
        'message', 'ip_address', 'user_agent', 'created_at'
    ]
    extra = 0
    can_delete = False
    ordering = ['-created_at']

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'transaction_id', 'user', 'course', 'amount',
        'currency', 'status', 'payment_method', 'created_at'
    )
    list_filter = ('status', 'payment_method', 'currency', 'created_at')
    search_fields = ('transaction_id', 'user__username', 'course__title')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [PaymentLogInline]


@admin.register(PaymentLog)
class PaymentLogAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'payment', 'event_type', 'previous_status',
        'new_status', 'ip_address', 'created_at'
    )
    list_filter = ('event_type', 'created_at')
    search_fields = ('payment__transaction_id', 'message')
    readonly_fields = (
        'payment', 'event_type', 'previous_status', 'new_status',
        'message', 'ip_address', 'user_agent', 'created_at'
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
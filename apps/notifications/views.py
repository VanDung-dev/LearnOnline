from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages
from .models import Notification

class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notifications/list.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')

    def post(self, request, *args, **kwargs):
        # Mark all as read
        if 'mark_all_read' in request.POST:
            Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
            messages.success(request, "All notifications marked as read.")
        return redirect('notifications:list')

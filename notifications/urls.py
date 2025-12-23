from django.urls import path
from .api_views import NotificationListView, UnreadCountView, MarkReadView

app_name = 'notifications'

urlpatterns = [
    path('api/list/', NotificationListView.as_view(), name='api_list'),
    path('api/unread-count/', UnreadCountView.as_view(), name='api_unread_count'),
    path('api/<int:pk>/mark-read/', MarkReadView.as_view(), name='api_mark_read'),
]

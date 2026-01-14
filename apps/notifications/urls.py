from django.urls import path
from .api_views import NotificationListView as ApiNotificationListView, UnreadCountView, MarkReadView
from .views import NotificationListView

app_name = 'notifications'

urlpatterns = [
    path('', NotificationListView.as_view(), name='list'),
    path('api/list/', ApiNotificationListView.as_view(), name='api_list'),
    path('api/unread-count/', UnreadCountView.as_view(), name='api_unread_count'),
    path('api/<int:pk>/mark-read/', MarkReadView.as_view(), name='api_mark_read'),
]

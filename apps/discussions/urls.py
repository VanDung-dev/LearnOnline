from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import api_views

# API Router
router = DefaultRouter()
router.register(r'discussions', api_views.DiscussionViewSet, basename='api-discussion')
router.register(r'replies', api_views.ReplyViewSet, basename='api-reply')

app_name = 'discussions'

urlpatterns = [
    # Template Views
    path('courses/<slug:slug>/discussions/', views.DiscussionListView.as_view(), name='discussion_list'),
    path('courses/<slug:slug>/discussions/create/', views.DiscussionCreateView.as_view(), name='discussion_create'),
    path('courses/<slug:slug>/discussions/<int:pk>/', views.DiscussionDetailView.as_view(), name='discussion_detail'),
    
    # API URLs included here for convenience in one app url config, or can be separated
    path('api/', include(router.urls)),
]

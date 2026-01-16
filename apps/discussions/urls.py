from django.urls import path
from . import views

app_name = 'discussions'


urlpatterns = [
    # Template Views
    path('courses/<slug:slug>/discussions/', views.DiscussionListView.as_view(), name='discussion_list'),
    path('courses/<slug:slug>/discussions/create/', views.DiscussionCreateView.as_view(), name='discussion_create'),
    path('courses/<slug:slug>/discussions/<int:pk>/', views.DiscussionDetailView.as_view(), name='discussion_detail'),
]

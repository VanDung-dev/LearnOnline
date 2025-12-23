from django.urls import path
from .api_views import StudentAnalyticsView, InstructorAnalyticsView

app_name = 'analytics'

urlpatterns = [
    path('api/student-progress/', StudentAnalyticsView.as_view(), name='student_progress'),
    path('api/instructor-stats/', InstructorAnalyticsView.as_view(), name='instructor_stats'),
]

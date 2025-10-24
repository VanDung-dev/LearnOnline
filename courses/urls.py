from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.home, name='home'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/<slug:slug>/', views.course_detail, name='course_detail'),
    path('courses/<slug:slug>/enroll/', views.enroll_course, name='enroll_course'),
    path('courses/<slug:course_slug>/lessons/<slug:lesson_slug>/', views.lesson_detail, name='lesson_detail'),
    path('courses/<slug:course_slug>/certificate/', views.course_certificate, name='course_certificate'),
    
    # Instructor URLs
    path('instructor/courses/', views.instructor_courses, name='instructor_courses'),
    path('instructor/courses/create/', views.create_course, name='create_course'),
    path('instructor/courses/<slug:slug>/edit/', views.edit_course, name='edit_course'),
    path('instructor/courses/<slug:slug>/delete/', views.delete_course, name='delete_course'),
    path('instructor/courses/<slug:course_slug>/modules/create/', views.create_module, name='create_module'),
    path('instructor/courses/<slug:course_slug>/modules/<int:module_id>/edit/', views.edit_module, name='edit_module'),
    path('instructor/courses/<slug:course_slug>/modules/<int:module_id>/lessons/create/', views.create_lesson, name='create_lesson'),
]
from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.home, name='home'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/<slug:slug>/', views.course_detail, name='course_detail'),
    path('courses/<slug:slug>/enroll/', views.enroll_course, name='enroll_course'),
    path('courses/<slug:course_slug>/lessons/<slug:lesson_slug>/', views.lesson_detail, name='lesson_detail'),
    path('courses/<slug:course_slug>/modules/<int:module_id>/lessons/<int:lesson_id>/reorder/', views.reorder_lessons, name='reorder_lessons'),
    path('courses/<slug:course_slug>/modules/<int:module_id>/lessons/create/', views.create_lesson, name='create_lesson'),
    path('courses/<slug:course_slug>/modules/<int:module_id>/lessons/<int:lesson_id>/edit/', views.edit_lesson, name='edit_lesson'),
    path('courses/<slug:course_slug>/modules/<int:module_id>/lessons/<int:lesson_id>/delete/', views.delete_lesson, name='delete_lesson'),
    path('courses/<slug:course_slug>/modules/<int:module_id>/lessons/<int:lesson_id>/video/delete/', views.delete_lesson_video, name='delete_lesson_video'),
    
    # Instructor URLs
    path('instructor/courses/', views.instructor_courses, name='instructor_courses'),
    path('instructor/courses/create/', views.create_course, name='create_course'),
    path('instructor/courses/<slug:slug>/edit/', views.edit_course, name='edit_course'),
    path('instructor/courses/<slug:slug>/delete/', views.delete_course, name='delete_course'),
    path('instructor/courses/<slug:course_slug>/modules/create/', views.create_module, name='create_module'),
    path('instructor/courses/<slug:course_slug>/modules/<int:module_id>/edit/', views.edit_module, name='edit_module'),
    path('instructor/courses/<slug:course_slug>/modules/<int:module_id>/delete/', views.delete_module, name='delete_module'),
    path('instructor/courses/<slug:course_slug>/reorder/', views.reorder_modules, name='reorder_modules'),
    
    # Quiz URLs with lesson dependency
    path('instructor/lessons/<int:lesson_id>/quiz/configure/', views.configure_quiz, name='configure_quiz'),

    # Standalone Quiz URLs (without lesson dependency)
    path('instructor/quizzes/configure/', views.configure_quiz, name='configure_quiz_standalone', kwargs={'lesson_id': None}),

    # Certificate URLs
    path('certificate/<str:certificate_id>/', views.course_certificate, name='course_certificate'),
    path('certificate/public/<str:certificate_id>/', views.public_certificate, name='public_certificate'),
    path('courses/<slug:slug>/purchase-certificate/', views.purchase_certificate, name='purchase_certificate'),
]
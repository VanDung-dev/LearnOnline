from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.home, name='home'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/search/autocomplete/', views.search_autocomplete, name='search_autocomplete'),
    path('courses/upload_image/', views.upload_image, name='upload_image'),
    path('courses/<slug:slug>/', views.course_detail, name='course_detail'),
    path('courses/<slug:slug>/learning-process/', views.course_learning_process, name='course_learning_process'),
    path('courses/<slug:slug>/enroll/', views.enroll_course, name='enroll_course'),
    path('courses/<slug:course_slug>/lessons/<slug:lesson_slug>/', views.lesson_detail, name='lesson_detail'),
    path('courses/<slug:course_slug>/modules/<int:module_id>/lessons/<int:lesson_id>/reorder/', views.reorder_lessons, name='reorder_lessons'),
    path('courses/<slug:course_slug>/modules/<int:module_id>/lessons/<int:lesson_id>/quiz/reorder/', views.reorder_quiz_questions, name='reorder_quiz_questions'),
    path('courses/<slug:course_slug>/modules/<int:module_id>/lessons/create/', views.create_lesson, name='create_lesson'),
    path('courses/<slug:course_slug>/modules/<int:module_id>/lessons/<int:lesson_id>/edit/', views.edit_lesson, name='edit_lesson'),
    path('courses/<slug:course_slug>/modules/<int:module_id>/lessons/<int:lesson_id>/delete/', views.delete_lesson, name='delete_lesson'),
    path('courses/<slug:course_slug>/modules/<int:module_id>/lessons/<int:lesson_id>/video/delete/', views.delete_lesson_video, name='delete_lesson_video'),
    
    # Instructor URLs
    path('dashboard/courses/list/legacy/', views.instructor_courses, name='instructor_courses'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/courses/create/', views.create_course, name='create_course'),
    path('dashboard/courses/create-category-ajax/', views.create_category_ajax, name='create_category_ajax'),
    path('dashboard/courses/<slug:slug>/edit/', views.edit_course, name='edit_course'),
    path('dashboard/courses/<slug:slug>/delete/', views.delete_course, name='delete_course'),
    path('dashboard/courses/<slug:course_slug>/modules/create/', views.create_module, name='create_module'),
    path('dashboard/courses/<slug:course_slug>/modules/<int:module_id>/edit/', views.edit_module, name='edit_module'),
    path('dashboard/courses/<slug:course_slug>/modules/<int:module_id>/delete/', views.delete_module, name='delete_module'),
    path('dashboard/courses/<slug:course_slug>/reorder/', views.reorder_modules, name='reorder_modules'),

    # Certificate URLs
    path('certificate/<str:certificate_id>/', views.course_certificate, name='course_certificate'),
    path('certificate/public/<str:certificate_id>/', views.public_certificate, name='public_certificate'),
    path('courses/<slug:slug>/purchase-certificate/', views.purchase_certificate, name='purchase_certificate'),
    
    # Support page
    path('support/', views.support, name='support'),
]
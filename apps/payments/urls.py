from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('course/<slug:course_slug>/pay/', views.payment_page, name='payment_page'),
    path('course/<slug:course_slug>/pay/<str:purchase_type>/', views.payment_page, name='payment_page_type'),
    path('course/<slug:course_slug>/process-payment/', views.process_payment, name='process_payment'),
    path('course/<slug:course_slug>/process-payment/<str:purchase_type>/', views.process_payment, name='process_payment_type'),
    path('success/<str:transaction_id>/', views.payment_success, name='payment_success'),
    path('webhook/<str:provider>/', views.payment_webhook, name='payment_webhook'),
]
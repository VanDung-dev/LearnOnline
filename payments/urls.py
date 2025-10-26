from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('course/<slug:course_slug>/pay/', views.payment_page, name='payment_page'),
    path('course/<slug:course_slug>/process-payment/', views.process_payment, name='process_payment'),
    path('course/<slug:course_slug>/purchase-certificate/', views.purchase_certificate_payment, name='purchase_certificate_payment'),
    path('course/<slug:course_slug>/process-certificate-payment/', views.process_certificate_payment, name='process_certificate_payment'),
]
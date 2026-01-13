from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', RedirectView.as_view(pattern_name='user_dashboard', permanent=False), name='profile'),
    path('profile/edit/', RedirectView.as_view(pattern_name='edit_profile', permanent=False)),
]
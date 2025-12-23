"""
URL configuration for DjangoProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', RedirectView.as_view(url='/', permanent=True)),
    path('', include('courses.urls')),
    path('accounts/', include('accounts.urls')),
    path('payments/', include('payments.urls')),
    path('notifications/', include('notifications.urls')),
    path('api/', include('api.urls')),  # REST API
]

# Serve media files in development and production
# In production, it's recommended to serve media files via web server (nginx, Apache, CDN, etc.)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serve static files in development and production
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers
handler404 = 'courses.views.custom_page_not_found'
handler500 = 'courses.views.custom_server_error'
handler403 = 'courses.views.custom_permission_denied'
handler400 = 'courses.views.custom_bad_request'
handler405 = 'courses.views.custom_method_not_allowed'
handler408 = 'courses.views.custom_request_timeout'
handler429 = 'courses.views.custom_too_many_requests'
handler502 = 'courses.views.custom_bad_gateway'
handler503 = 'courses.views.custom_service_unavailable'
handler504 = 'courses.views.custom_gateway_timeout'
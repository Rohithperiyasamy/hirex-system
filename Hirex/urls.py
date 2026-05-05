"""URL configuration for Hirex project."""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('',      RedirectView.as_view(url='/hirex/', permanent=False), name='root_redirect'),
    path('admin/', admin.site.urls),
    path('',       include('Myapp.urls')),
    path('auth/',  include('Authentication.urls')),
    path('hr/',    include('Hr.urls')),
]

"""
URL configuration for Bar Customer Intelligence project.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('src.api.urls')),
]
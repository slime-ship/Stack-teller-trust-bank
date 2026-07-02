"""
URL configuration for wealthbridge project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
import os
from django.conf import settings
from django.http import HttpResponse, Http404
from django.contrib import admin
from django.urls import path, include

def serve_static_root(request, filename, content_type):
    filepath = os.path.join(settings.BASE_DIR, 'static', filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return HttpResponse(content, content_type=content_type)
    raise Http404("File not found")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sw.js', lambda r: serve_static_root(r, 'sw.js', 'application/javascript'), name='sw_js'),
    path('manifest.json', lambda r: serve_static_root(r, 'manifest.json', 'application/json'), name='manifest_json'),
    path('', include("bank_app.urls"))
]

"""
URL configuration for mitasa project.

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
from django.contrib import admin
from django.urls import path, include
from .views import index
from user.views import login_view as login
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', login, name='index'),
    path('', include('helper.urls')),
    path('user/', include('user.urls')),
    path('claim/', include('claim.urls')),
    path('staff/', include('mitasa_admin.urls')),
    path('medical/', include('medical_claim.urls')),
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

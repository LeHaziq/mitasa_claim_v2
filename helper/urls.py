from django.urls import path
from . import views

app_name = "helper"

urlpatterns = [
    path('download/<path:file>', views.download, name='download')
]

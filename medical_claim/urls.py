from django.urls import path
from . import views

app_name = "medical"

urlpatterns = [
    path('dashboard/', views.medical_dashboard, name='dashboard')
]

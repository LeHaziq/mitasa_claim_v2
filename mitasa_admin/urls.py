from django.urls import path
from . import views

app_name = "mitasa_admin"

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name="dashboard")
]

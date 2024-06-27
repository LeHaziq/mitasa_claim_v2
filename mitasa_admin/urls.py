from django.urls import path
from . import views

app_name = "mitasa_admin"

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name="dashboard"),
    path('history/', views.admin_history, name="history"),
    path('history/<int:year>', views.history_admin_dashboard, name="history_dashboard"),
    path('user/<int:user_id>', views.user_dashboard, name="user_dashboard"),
]

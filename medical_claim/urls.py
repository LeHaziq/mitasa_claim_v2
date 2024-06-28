from django.urls import path
from . import views

app_name = "medical"

urlpatterns = [
    path('dashboard/', views.medical_dashboard, name='dashboard'),
    path('submit/', views.medical_submit, name='submit'),
    path('detail/<int:claim_id>', views.medical_detail, name='detail'),
    path('history/', views.medical_history, name='history'),
    path('history/<int:year>', views.medical_history_dashboard, name='history_dashboard'),
]

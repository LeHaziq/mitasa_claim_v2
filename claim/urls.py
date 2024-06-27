from django.urls import path
from . import views

app_name = "claim"

urlpatterns = [
    path('dashboard/', views.claim_dashboard, name="dashboard"),
    path('submit/', views.claim_submit, name="submit"),
    path('detail/<int:claim_id>', views.claim_detail, name="detail"),
    path('delete/<int:claim_id>', views.claim_delete, name="delete"),
    path('history/', views.claim_history, name="history"),
]
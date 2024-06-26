from django.urls import path
from . import views

app_name = "claim"

urlpatterns = [
    path('dashboard/', views.claim_dashboard, name="dashboard"),
    path('submit/', views.claim_submit, name="submit")
]
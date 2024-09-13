from django.urls import path
from . import views

app_name = "user"

urlpatterns = [
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),
    path('profile/', views.profile_view, name="profile"),
    path('profile/new', views.profile_new, name="profile_new"),
    path('profile/edit', views.user_edit, name="edit"),
    path('profile/details/edit', views.profile_edit, name="profile_edit"),
    path('password/change', views.password_change, name="password_change"),
]
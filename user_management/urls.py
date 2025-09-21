from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('user_home/', views.user_home, name='user_home'),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.login_view, name="login"),
    path('logout/', views.logout_view, name='logout'),
    path("edit-profile/", views.edit_profile, name="edit_profile"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    # Password Reset URLs
    path("password-reset/", auth_views.PasswordResetView.as_view(), name="password_reset"),
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
    # Email Verification
    path("verify-email/<uidb64>/<token>/", views.VerifyEmailView.as_view(), name="verify_email"),
]

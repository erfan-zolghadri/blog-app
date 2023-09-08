from django.contrib.auth.views import LogoutView
from django.urls import path

from accounts.views import (
    RegisterUserView,
    VerifyAccountView,
    LoginView,
    UserUpdateView,
    Dashboard,
    PasswordChangeView,
    PasswordResetView,
    PasswordResetConfirmView
)

app_name = "accounts"

urlpatterns = [
    path("register/", view=RegisterUserView.as_view(), name="register-user"),
    path(
        "verify/<str:uidb64>/<str:token>/",
        view=VerifyAccountView.as_view(),
        name="verify-account"
    ),

    path("login/", view=LoginView.as_view(), name="login"),
    path("logout/", view=LogoutView.as_view(), name="logout"),

    path(
        "reset-password/",
        PasswordResetView.as_view(),
        name="reset-password"
    ),
    path(
        "reset-password-confirm/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(),
        name="reset-password-confirm"
    ),

    path(
        "dashboard/change-password/",
        view=PasswordChangeView.as_view(),
        name="change-password"
    ),
    path("dashboard/edit/", view=UserUpdateView.as_view(), name="user-update"),
    path("dashboard/", view=Dashboard.as_view(), name="dashboard"),
]

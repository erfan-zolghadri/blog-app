from django.urls import path
from django.contrib.auth.views import LogoutView
from accounts.views import (
    user_create,
    verify_account,
    LoginView,
    user_update,
    Dashboard,
    PasswordChangeView,
    PasswordResetView,
    PasswordResetConfirmView
)

urlpatterns = [
    path("register/", view=user_create, name="user_create"),
    path(
        "verify/<str:uidb64>/<str:token>/",
        view=verify_account,
        name="verify_account"
    ),

    path("login/", view=LoginView.as_view(), name="login"),
    path("logout/", view=LogoutView.as_view(), name="logout"),

    path(
        "reset-password/",
        PasswordResetView.as_view(),
        name="reset_password"
    ),
    path(
        "reset-password-confirm/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(),
        name="reset_password_confirm"
    ),

    path("dashboard/", view=Dashboard.as_view(), name="dashboard"),
    path("dashboard/edit/", view=user_update, name="user_update"),
    path(
        "dashboard/change-password/",
        view=PasswordChangeView.as_view(),
        name="change_password"
    ),
]

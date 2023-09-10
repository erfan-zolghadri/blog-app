from django.contrib.auth.views import LogoutView
from django.urls import path

from accounts import views

app_name = 'accounts'

urlpatterns = [
    path(
        'register/',
        views.RegisterUserView.as_view(),
        name='register-user'
    ),
    path(
        'verify/<str:uidb64>/<str:token>/',
        views.VerifyAccountView.as_view(),
        name='verify-account'
    ),

    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path(
        'reset-password/',
        views.PasswordResetView.as_view(),
        name='reset-password'
    ),
    path(
        'reset-password-confirm/<uidb64>/<token>/',
        views.PasswordResetConfirmView.as_view(),
        name='reset-password-confirm'
    ),

    path(
        'dashboard/change-password/',
        views.PasswordChangeView.as_view(),
        name='change-password'
    ),
    path(
        'dashboard/edit/',
        views.UserUpdateView.as_view(),
        name='user-update'
    ),
    path('dashboard/', views.Dashboard.as_view(), name='dashboard'),
]

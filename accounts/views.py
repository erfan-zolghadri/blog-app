from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import (
    LoginView as BaseLoginView,
    PasswordChangeView as BasePasswordChangeView,
    PasswordResetView as BasePasswordResetView,
    PasswordResetConfirmView as BasePasswordResetConfirmView
)
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from accounts.forms import (
    AuthenticationForm,
    UserCreationForm,
    UserChangeForm,
    PasswordChangeForm
)
from django.views.generic.base import TemplateView
from accounts.utilities import send_verification_email


def user_create(request):
    if request.user.is_authenticated:
        return redirect("index")

    if request.method == "POST":
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            email_subject = "Account Verification"
            email_template = "accounts/registration/verification_email.html"
            send_verification_email(
                request,
                user,
                email_subject,
                email_template
            )

            messages.info(
                request,
                "The verification link has been sent to your email."
            )
            return redirect("login")
    else:
        form = UserCreationForm()

    context = {"form": form}
    return render(request, "accounts/registration/user_create.html", context)


def verify_account(request, uidb64, token):
    try:
        user_id = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(id=user_id)
    except (
        TypeError, ValueError, OverflowError,
        get_user_model().DoesNotExist
    ):
        user = None

    if (
        (user is not None) and
        (default_token_generator.check_token(user, token))
    ):
        user.is_active = True
        user.save()

        # Add user to group
        group = get_object_or_404(Group, name="Blog - Post Managers")
        group.user_set.add(user)

        messages.success(
            request,
            "Your account has been successfully verified."
        )
    else:
        messages.error(request, "The link has been expired!")

    return redirect("login")


class LoginView(BaseLoginView):
    template_name = "accounts/login.html"
    form_class = AuthenticationForm
    redirect_authenticated_user = True


@login_required
def user_update(request):
    if request.method == "POST":
        form = UserChangeForm(data=request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                _("Your profile has been successfully edited.")
            )
            return redirect("dashboard")
    else:
        form = UserChangeForm(instance=request.user)

    context = {"form": form}
    return render(request, "accounts/user_update.html", context)


class PasswordChangeView(
    LoginRequiredMixin,
    SuccessMessageMixin,
    BasePasswordChangeView
):
    template_name = "accounts/password/change_password.html"
    form_class = PasswordChangeForm
    success_url = reverse_lazy("dashboard")
    success_message = "Your password has been successfully changed."


class PasswordResetView(SuccessMessageMixin, BasePasswordResetView):
    template_name = "accounts/password/reset_password.html"
    success_url = reverse_lazy("login")
    email_template_name = "accounts/password/reset_password_email.html"
    subject_template_name = "accounts/password/reset_password_subject.txt"
    success_message = "Password reset link was sent to your email."


class PasswordResetConfirmView(
    SuccessMessageMixin,
    BasePasswordResetConfirmView
):
    template_name = "accounts/password/reset_password_confirm.html"
    success_url = reverse_lazy("login")
    success_message = "Your password has been successfully reset."


class Dashboard(LoginRequiredMixin, TemplateView):
    template_name = "accounts/dashboard.html"

from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import get_user_model
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
from django.views.generic.base import RedirectView
from django.views.generic.edit import FormView, UpdateView
from accounts.forms import (
    AuthenticationForm,
    UserCreationForm,
    UserChangeForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm
)
from django.views.generic.base import TemplateView
from accounts.utilities import send_verification_email


class RegisterUserView(SuccessMessageMixin, FormView):
    model = get_user_model()
    form_class = UserCreationForm
    template_name = "accounts/registration/register_user.html"
    success_url = reverse_lazy("accounts:login")
    success_message = _("The verification link has been sent to your email.")

    def dispatch(self, request, *args, **kwargs):
        """
        Prevent authenticated user to access register URL.
        """
        if request.user.is_authenticated:
            return redirect("accounts:dashboard")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        email_subject = "Account Verification"
        email_template = "accounts/registration/verification_email.html"
        send_verification_email(
            self.request,
            user,
            email_subject,
            email_template
        )

        return super().form_valid(form)


class VerifyAccountView(RedirectView):
    url = reverse_lazy("accounts:login")

    def get_redirect_url(self, *args, **kwargs):
        try:
            user_id = urlsafe_base64_decode(self.kwargs["uidb64"]).decode()
            user = get_user_model().objects.get(id=user_id)
        except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
            user = None

        if (
            (user is not None) and
            default_token_generator.check_token(user, self.kwargs["token"])
        ):
            user.is_active = True
            user.save()

            # Add user to group
            group = get_object_or_404(Group, name="Blog - Post Managers")
            group.user_set.add(user)

            messages.success(self.request, _("Your account has been successfully verified."))
        else:
            messages.error(self.request, _("The link has been expired!"))
        return super().get_redirect_url(*args, **kwargs)


class LoginView(BaseLoginView):
    form_class = AuthenticationForm
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = get_user_model()
    form_class = UserChangeForm
    template_name = "accounts/user_update.html"
    success_url = reverse_lazy("accounts:dashboard")
    success_message = _("Your profile has been successfully edited.")

    def get_object(self, queryset=None):
        return self.request.user


class PasswordChangeView(SuccessMessageMixin, BasePasswordChangeView):
    form_class = PasswordChangeForm
    template_name = "accounts/password/change_password.html"
    success_url = reverse_lazy("accounts:dashboard")
    success_message = _("Your password has been successfully changed.")


class PasswordResetView(SuccessMessageMixin, BasePasswordResetView):
    form_class = PasswordResetForm
    template_name = "accounts/password/reset_password.html"
    success_url = reverse_lazy("accounts:login")
    email_template_name = "accounts/password/reset_password_email.html"
    subject_template_name = "accounts/password/reset_password_subject.txt"
    success_message = _("Password reset link was sent to your email.")


class PasswordResetConfirmView(SuccessMessageMixin, BasePasswordResetConfirmView):
    form_class = SetPasswordForm
    template_name = "accounts/password/reset_password_confirm.html"
    success_url = reverse_lazy("accounts:login")
    success_message = _("Your password has been successfully reset.")


class Dashboard(LoginRequiredMixin, TemplateView):
    template_name = "accounts/dashboard.html"

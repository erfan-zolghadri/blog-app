from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm as BaseAuthenticationForm,
    BaseUserCreationForm,
    UserChangeForm as BaseUserChangeForm,
    PasswordChangeForm as BasePasswordChangeForm
)
from django.utils.translation import gettext_lazy as _

user_model = get_user_model()


class UserCreationForm(BaseUserCreationForm):
    error_messages = {
        "password_mismatch": _("Make sure your passwords match."),
    }

    class Meta:
        model = user_model
        fields = [
            "email", "username", "first_name",
            "last_name", "password1", "password2"
        ]


class AuthenticationForm(BaseAuthenticationForm):
    error_messages = {
        "invalid_login": _(
            "Please enter a correct %(username)s and password."
        ),
    }

    def __init__(self, *args, **kwargs):
        super(AuthenticationForm, self).__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({
            "placeholder": _("Email address")
        })
        self.fields["password"].widget.attrs.update({
            "placeholder": _("Password")
        })


class UserChangeForm(BaseUserChangeForm):
    class Meta:
        model = user_model
        fields = ["email", "username", "first_name", "last_name"]

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"


class PasswordChangeForm(BasePasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"

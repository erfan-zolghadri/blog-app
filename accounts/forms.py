from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    BaseUserCreationForm,
    UserChangeForm as BaseUserChangeForm,
    PasswordChangeForm as BasePasswordChangeForm,
    PasswordResetForm as BasePasswordResetForm,
    SetPasswordForm as BaseSetPasswordForm
)
from django.utils.translation import gettext_lazy as _

from core.forms import BootstrapyForm

user_model = get_user_model()


class RegisterUserForm(BaseUserCreationForm, BootstrapyForm):
    error_messages = {
        'password_mismatch': _('Make sure your passwords match.'),
    }

    class Meta:
        model = user_model
        fields = [
            'email', 'username', 'first_name',
            'last_name', 'password1', 'password2'
        ]


class LoginForm(AuthenticationForm, BootstrapyForm):
    error_messages = {
        'invalid_login': _(
            'Please enter a correct %(username)s and password.'
        ),
    }

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'placeholder': _('Email address')
        })
        self.fields['password'].widget.attrs.update({
            'placeholder': _('Password')
        })


class UserChangeForm(BaseUserChangeForm, BootstrapyForm):
    class Meta:
        model = user_model
        fields = [
            'email', 'username', 'first_name',
            'last_name', 'image', 'bio'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 5})
        }


class PasswordChangeForm(BasePasswordChangeForm, BootstrapyForm):
    pass


class PasswordResetForm(BasePasswordResetForm, BootstrapyForm):
    pass


class SetPasswordForm(BaseSetPasswordForm, BootstrapyForm):
    pass

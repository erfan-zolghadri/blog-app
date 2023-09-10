from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from guardian.mixins import GuardianUserMixin


class UserManager(BaseUserManager):
    def create_user(
        self,
        email,
        username,
        first_name,
        last_name,
        password=None,
        **extra_fields
    ):
        if not email:
            raise ValueError('Users must have an email address.')

        if not username:
            raise ValueError('Users must have an username.')

        if not first_name:
            raise ValueError('Users must have an first_name.')

        if not last_name:
            raise ValueError('Users must have an last_name.')

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        email,
        username,
        first_name,
        last_name,
        password=None,
        **extra_fields
    ):
        user = self.create_user(
            email,
            username,
            first_name,
            last_name,
            password,
            **extra_fields
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin, GuardianUserMixin):
    username_validator = UnicodeUsernameValidator()

    email = models.EmailField(
        verbose_name=_('email address'),
        max_length=255,
        unique=True,
        error_messages={
            'unique': _('A user with that email address already exists.')
        }
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[username_validator],
        help_text=_(
            '150 characters or fewer. Letters, digits and @/./+/-/_ only.'
        ),
        error_messages={
            'unique': _('A user with that username already exists.')
        }
    )
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    is_active = models.BooleanField(
        verbose_name=_('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        )
    )
    is_staff = models.BooleanField(
        verbose_name=_('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'
        )
    )
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def get_short_name(self):
        return self.first_name

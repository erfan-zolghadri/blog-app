from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

user_model = get_user_model()


@admin.register(user_model)
class UserAdmin(BaseUserAdmin):
    list_display = [
        'email', 'username', 'is_active',
        'is_staff', 'is_superuser'
    ]
    fieldsets = [
        [
            None,
            {
                'fields': [
                    'email', 'username', 'first_name',
                    'last_name', 'image', 'bio', 'password'
                ]
            },
        ],
        [
            _('Permissions'),
            {
                'fields': [
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions'
                ]
            }
        ],
        [
            _('Dates'),
            {
                'classes': ['collapse'],
                'fields': ['last_login', 'date_joined']
            }
        ]
    ]
    add_fieldsets = [
        [
            None,
            {
                'fields': [
                    'email', 'username', 'first_name', 'last_name',
                    'password1', 'password2'
                ]
            }
        ]
    ]
    readonly_fields = ['password', 'last_login', 'date_joined']
    search_fields = ['email', 'username']

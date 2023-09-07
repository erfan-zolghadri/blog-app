from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from guardian.admin import GuardedModelAdmin

from blog.models import Post, Tag


@admin.register(Post)
class PostAdmin(GuardedModelAdmin):
    list_display = ["title", "views", "is_active", "user"]
    prepopulated_fields = {"slug": ["title"]}
    list_editable = ["is_active"]
    readonly_fields = ["views", "created_at", "updated_at"]
    search_fields = ["title"]
    list_filter = ["is_active"]
    fieldsets = [
        [
            None,
            {
                "fields": [
                    "slug", "title", "content", "is_active", "user",
                    "views", "tags", "image", "bookmarks", "likes"
                ]
            },
        ],
        [
            _("Dates"),
            {
                "fields": ["created_at", "updated_at"],
                "classes": ["collapse"]
            }
        ],
    ]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ["name"]}
    readonly_fields = ["created_at", "updated_at"]
    search_fields = ["name"]
    fieldsets = [
        [
            None,
            {"fields": ["slug", "name"]},
        ],
        [
            _("Dates"),
            {
                "fields": ["created_at", "updated_at"],
                "classes": ["collapse"]
            }
        ],
    ]

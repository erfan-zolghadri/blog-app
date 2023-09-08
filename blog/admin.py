from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from guardian.admin import GuardedModelAdmin

from blog.models import Category, Comment, Post, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]
    prepopulated_fields = {"slug": ["name"]}
    readonly_fields = ["created_at", "updated_at"]
    search_fields = ["name"]
    fieldsets = [
        [
            None,
            {
                "fields": ["name", "slug"]
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


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["post", "user", "is_active"]
    readonly_fields = ["content", "created_at", "updated_at", "post", "user"]
    search_fields = ["post__title", "user__email", "user__username"]
    list_filter = ["is_active"]
    fieldsets = [
        [
            None,
            {
                "fields": [
                    "content", "is_active", "post", "user",
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


@admin.register(Post)
class PostAdmin(GuardedModelAdmin):
    list_display = [
        "title", "views", "status", "user",
        "category", "is_active"
    ]
    prepopulated_fields = {"slug": ["title"]}
    readonly_fields = ["views", "created_at", "updated_at"]
    search_fields = ["title", "category__name"]
    list_filter = ["status", "is_active", "category"]
    fieldsets = [
        [
            None,
            {
                "fields": [
                    "title", "slug", "content", "image", "status", "is_active",
                    "views", "user", "category", "tags", "bookmarks", "likes"
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

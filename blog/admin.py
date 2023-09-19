from django.contrib import admin
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode
from django.utils.translation import gettext_lazy as _

from guardian.admin import GuardedModelAdmin
from mptt.admin import MPTTModelAdmin

from blog.models import Category, Comment, Post, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'title']
    list_per_page = 20
    prepopulated_fields = {'slug': ['title']}
    readonly_fields = ['created_at', 'updated_at']
    list_display_links = ['id', 'title']
    ordering = ['title']
    search_fields = ['title__istartswith']
    fieldsets = [
        [
            None,
            {
                'fields': ['title', 'description', 'slug']
            },
        ],
        [
            _('Dates'),
            {
                'fields': ['created_at', 'updated_at'],
                'classes': ['collapse']
            }
        ],
    ]


@admin.register(Comment)
class CommentAdmin(MPTTModelAdmin):
    list_display = ['id', 'post', 'user', 'status']
    list_per_page = 20
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['status']
    list_filter = ['status']
    search_fields = [
        'post__title', 'user__email__istartswith',
        'user__username__istartswith']
    fieldsets = [
        [
            None,
            {
                'fields': [
                    'content', 'status', 'post', 'user', 'parent'
                ]
            },
        ],
        [
            _('Dates'),
            {
                'fields': ['created_at', 'updated_at'],
                'classes': ['collapse']
            }
        ],
    ]


@admin.register(Post)
class PostAdmin(GuardedModelAdmin):
    list_display = [
        'id', 'title', 'views', 'user', 'category',
        'comments_count', 'is_active', 'status'
    ]
    list_per_page = 20
    prepopulated_fields = {'slug': ['title']}
    readonly_fields = ['views', 'created_at', 'updated_at']
    list_display_links = ['id', 'title']
    list_editable = ['is_active', 'status']
    search_fields = [
        'title', 'category__title__istartswith',
        'user__email__istartswith'
    ]
    list_filter = ['status', 'is_active']
    fieldsets = [
        [
            None,
            {
                'fields': [
                    'title', 'slug', 'content', 'image', 'status', 'is_active',
                    'views', 'user', 'category', 'tags', 'bookmarks', 'likes'
                ]
            },
        ],
        [
            _('Dates'),
            {
                'fields': ['created_at', 'updated_at'],
                'classes': ['collapse']
            }
        ],
    ]

    def get_queryset(self, request):
        return super().get_queryset(request) \
            .prefetch_related('comments') \
            .annotate(comments_count=Count('comments'))
    
    @admin.display(description='# comments', ordering='comments_count')
    def comments_count(self, post):
        url = (
            reverse('admin:blog_comment_changelist')
            + '?'
            + urlencode({'post_id': post.id})
        )
        return format_html(
            '<a href={url}>{comments_count}</a>',
            url=url,
            comments_count=post.comments_count
        )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']
    list_per_page = 20
    prepopulated_fields = {'slug': ['name']}
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']
    search_fields = ['name__istartswith']
    fieldsets = [
        [
            None,
            {'fields': ['slug', 'name']},
        ],
        [
            _('Dates'),
            {
                'fields': ['created_at', 'updated_at'],
                'classes': ['collapse']
            }
        ],
    ]

from django.contrib import admin
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode
from django.utils.translation import gettext_lazy as _

from guardian.admin import GuardedModelAdmin
from mptt.admin import MPTTModelAdmin

from blog.models import Category, Comment, Post, Tag


def pluralize_objects(objects_count):
    if objects_count == 1:
        return ' was'
    return 's were'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'posts_count']
    list_display_links = ['id', 'title']
    list_per_page = 20
    prepopulated_fields = {'slug': ['title']}
    readonly_fields = ['created_at', 'updated_at']
    search_fields = ['title__istartswith']

    def get_queryset(self, request):
        return super().get_queryset(request) \
            .prefetch_related('posts') \
            .annotate(posts_count=Count('posts'))

    @admin.display(description='#posts', ordering='posts_count')
    def posts_count(self, category):
        url = (
            reverse('admin:blog_post_changelist')
            + '?'
            + urlencode({'category_id': category.id})
        )
        return format_html(
            '<a href="{url}">{posts_count}</a>',
            url=url,
            posts_count=category.posts_count
        )


@admin.register(Comment)
class CommentAdmin(MPTTModelAdmin):
    list_display = ['id', 'post', 'user', 'status']
    list_editable = ['status']
    list_filter = ['status']
    list_per_page = 20
    autocomplete_fields = ['post', 'user', 'parent']
    readonly_fields = ['created_at', 'updated_at']
    search_fields = ['id']
    actions = ['set_as_pending', 'set_as_approved', 'set_as_not_approved']

    @admin.action(description='Set as pending')
    def set_as_pending(self, request, queryset):
        updated_counts = queryset.update(status=Comment.COMMENT_STATUS_PENDING)
        pluralized_comments = pluralize_objects(updated_counts)

        self.message_user(
            request,
            message=f'{updated_counts} comment{pluralized_comments} set as pending.'
        )

    @admin.action(description='Set as approved')
    def set_as_approved(self, request, queryset):
        updated_counts = queryset.update(status=Comment.COMMENT_STATUS_APPROVED)
        pluralized_comments = pluralize_objects(updated_counts)

        self.message_user(
            request,
            message=f'{updated_counts} comment{pluralized_comments} set as approved.'
        )

    @admin.action(description='Set as not approved')
    def set_as_not_approved(self, request, queryset):
        updated_counts = queryset.update(status=Comment.COMMENT_STATUS_NOT_APPROVED)
        pluralized_comments = pluralize_objects(updated_counts)

        self.message_user(
            request,
            message=f'{updated_counts} comment{pluralized_comments} set as not approved.'
        )


@admin.register(Post)
class PostAdmin(GuardedModelAdmin):
    list_display = [
        'id', 'title', 'views', 'user', 'category',
        'comments_count', 'is_active', 'status'
    ]
    list_display_links = ['id', 'title']
    list_editable = ['is_active', 'status']
    list_filter = ['status', 'is_active']
    list_per_page = 20
    autocomplete_fields = ['user', 'category']
    prepopulated_fields = {'slug': ['title']}
    readonly_fields = ['views', 'created_at', 'updated_at']
    search_fields = ['title']
    actions = ['set_as_published', 'set_as_draft']

    def get_queryset(self, request):
        return super().get_queryset(request) \
            .prefetch_related('comments') \
            .annotate(comments_count=Count('comments'))
    
    @admin.display(description='#comments', ordering='comments_count')
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
    
    @admin.action(description='Set as published')
    def set_as_published(self, request, queryset):
        updated_counts = queryset.update(status=Post.POST_STATUS_PUBLISHED)
        pluralized_posts = pluralize_objects(updated_counts)

        self.message_user(
            request,
            message=f'{updated_counts} comment{pluralized_posts} set as published.'
        )

    @admin.action(description='Set as draft')
    def set_as_draft(self, request, queryset):
        updated_counts = queryset.update(status=Post.POST_STATUS_DRAFT)
        pluralized_posts = pluralize_objects(updated_counts)

        self.message_user(
            request,
            message=f'{updated_counts} comment{pluralized_posts} set as draft.'
        )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_display_links = ['id', 'name']
    list_per_page = 20
    prepopulated_fields = {'slug': ['name']}
    readonly_fields = ['created_at', 'updated_at']
    search_fields = ['name__istartswith']

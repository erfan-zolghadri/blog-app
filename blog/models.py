from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from mptt.models import MPTTModel, TreeForeignKey


def post_media_directory(instance, filename):
    return f'blog/posts/{instance.id}/{filename}'


class Category(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['title']

    def __str__(self):
        return self.title


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        return super(Tag, self).save(*args, **kwargs)


class PublishedPostManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset() \
            .select_related('user') \
            .prefetch_related('tags') \
            .filter(status=Post.POST_STATUS_PUBLISHED, is_active=True)


class Post(models.Model):
    POST_STATUS_DRAFT = 'draft'
    POST_STATUS_PUBLISHED = 'published'
    POST_STATUS = [
        (POST_STATUS_DRAFT, 'Draft'),
        (POST_STATUS_PUBLISHED, 'Published')
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    content = models.TextField()
    image = models.ImageField(
        upload_to=post_media_directory,
        null=True,
        blank=True,
        default='blog/posts/default.png'
    )
    views = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=50,
        choices=POST_STATUS,
        default=POST_STATUS_DRAFT
    )
    is_active = models.BooleanField(verbose_name='active', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='posts'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='posts'
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    bookmarks = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='bookmarks'
    )
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='likes'
    )

    objects = models.Manager()
    published = PublishedPostManager()

    class Meta:
        ordering = ['-created_at']
        permissions = [('olp_blog_change_post', 'OLP - Can change post')]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.title)
        return super(Post, self).save(*args, **kwargs)

    def delete(self):
        self.is_active = False
        self.save()

    def get_absolute_url(self):
        return reverse('blog:post-detail', kwargs={'slug': self.slug})


class Comment(MPTTModel):
    COMMENT_STATUS_PENDING = 'pending'
    COMMENT_STATUS_APPROVED = 'approved'
    COMMENT_STATUS_NOT_APPROVED = 'not approved'
    COMMENT_STATUS = [
        (COMMENT_STATUS_PENDING, 'Pending'),
        (COMMENT_STATUS_APPROVED, 'Approved'),
        (COMMENT_STATUS_NOT_APPROVED, 'Not approved')
    ]

    content = models.TextField()
    status = models.CharField(
        max_length=50,
        choices=COMMENT_STATUS,
        default=COMMENT_STATUS_PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )

    class MPTTMeta:
        order_insertion_by=['created_at']

    def __str__(self):
        return f"by '{self.user.email}' on '{self.post.title}'"

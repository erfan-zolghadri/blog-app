from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


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


class Post(models.Model):
    DRAFT = "draft"
    PUBLISHED = "published"
    STATUS_CHOICES = [
        (DRAFT, "Draft"),
        (PUBLISHED, "Published")
    ]

    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField()
    image = models.ImageField(upload_to="blog/posts", null=True, blank=True)
    views = models.IntegerField(default=0)
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default=DRAFT
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts"
    )
    tags = models.ManyToManyField(Tag, related_name="posts", blank=True)
    bookmarks = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="bookmarks",
        blank=True
    )
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="likes",
        blank=True
    )

    class Meta:
        verbose_name = _("post")
        verbose_name_plural = _("posts")
        ordering = ["-created_at"]
        permissions = [("olp_blog_change_post", "OLP - Can change post")]

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
        return reverse("blog:post-detail", kwargs={"slug": self.slug})


class Comment(models.Model):
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    class Meta:
        verbose_name = _("comment")
        verbose_name_plural = _("comments")
        ordering = ["-created_at"]

    def __str__(self):
        return f"by '{self.user.email}' on '{self.post.title}'"

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


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
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField()
    image = models.ImageField(
        upload_to="blog/posts",
        null=True,
        blank=True
    )
    views = models.IntegerField(default=0)
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
        permissions = [
            ("olp_blog_change_post", "OLP - Can change post")
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.title)
        return super(Post, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:post-detail", kwargs={"slug": self.slug})


# class Comment(models.Model):
#     content = models.TextField()
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     post = models.ForeignKey(
#         Post,
#         on_delete=models.CASCADE,
#         related_name="comments"
#     )
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="comments",
#         null=True,
#         blank=True
#     )

#     def __str__(self):
#         return f"{self.user.email}"

#     @property
#     def full_name(self):
#         return f"{self.user.first_name} {self.user.last_name}"

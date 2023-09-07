from django.core.exceptions import PermissionDenied
<<<<<<< HEAD
from django.shortcuts import redirect, get_object_or_404
=======
from django.db.models import Count, Q, F
>>>>>>> feature
from django.contrib.auth import get_user_model
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
<<<<<<< HEAD
=======

>>>>>>> feature
from guardian.shortcuts import (
    assign_perm,
    get_objects_for_user,
    get_user_perms
)

from accounts.mixins import UserAccessMixin
from blog.forms import PostForm
from blog.models import Post, Tag


class PostListView(ListView):
    model = Post
    context_object_name = "posts"
    template_name = "blog/post_list.html"
    paginate_by = 9

    def get_queryset(self):
        return Post.objects. \
            select_related("user"). \
            prefetch_related("tags"). \
            filter(is_active=True). \
            order_by("-created_at")


class PostDetailView(DetailView):
    model = Post
    context_object_name = "post"
    template_name = "blog/post_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object

        # Update post views
        post.views = F("views") + 1
        post.save()
        post.refresh_from_db()

        post_tags = post.tags.all()

        # Get post object-level permission
        post_perms = None
        if self.request.user.is_authenticated:
            post_perms = get_user_perms(user=self.request.user, obj=post)

        related_posts = Post.objects.filter(
            is_active=True,
            user=post.user
        ).exclude(pk=post.pk)[:3]

        top_users = get_user_model().objects. \
            annotate(posts_count=Count("posts")). \
            filter(posts_count__gt=0) .\
            order_by("-posts_count")[:3]
        
        top_tags = Tag.objects. \
            annotate(posts_count=Count("posts")). \
            filter(posts_count__gt=0). \
            order_by("-posts_count")[:5]

        context.update({
            "post_tags": post_tags,
            "post_perms": post_perms,
            "related_posts": related_posts,
            "top_users": top_users,
            "top_tags": top_tags
        })
        return context


class PostCreateView(UserAccessMixin, SuccessMessageMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_create_update.html"
    success_url = reverse_lazy("blog:my-post-list")
    success_message = _("Your post has been successfully created.")
    permission_required = "blog.add_post"

    def form_valid(self, form):
        post = form.save(commit=False)
        post.user = self.request.user
        post.save()

        # Save m2m relationship (tags)
        form.save_m2m()

        # Assign OLP permission to user
        assign_perm(
            perm="olp_blog_change_post",
            user_or_group=self.request.user,
            obj=post
        )

        return super().form_valid(form)


class PostUpdateView(UserAccessMixin, SuccessMessageMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_create_update.html"
    success_url = reverse_lazy("blog:my-post-list")
    permission_required = "blog.change_post"
    success_message = _("Your post has been successfully edited.")

    def dispatch(self, request, *args, **kwargs):
        """
        Check user has object-level permission (change) on post.
        """
        post = self.get_object()
        if not self.request.user.has_perm(perm="olp_blog_change_post", obj=post):
            return redirect("accounts:dashboard")
        return super().dispatch(request, *args, **kwargs)


class PostDeleteView(UserAccessMixin, SuccessMessageMixin, DeleteView):
    model = Post
    success_url = reverse_lazy("my-post-list")
    permission_required = "blog.delete_post"
    success_message = _("Your post has been successfully deleted.")

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        if not self.request.user.has_perm(
            perm="olp_blog_change_post",
            obj=post
        ):
            raise PermissionDenied()


class TagPostListView(ListView):
    tag = None
    model = Post
    context_object_name = "tag_posts"
    template_name = "blog/tag_post_list.html"
    paginate_by = 6

    def get_queryset(self):
        # Save tag to use in other queries
        self.tag = get_object_or_404(Tag, slug=self.kwargs["tag_slug"])

        return self.tag.posts. \
            select_related("user"). \
            prefetch_related("tags"). \
            filter(is_active=True). \
            order_by("-created_at")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        top_tags = Tag.objects.annotate(posts_count=Count("posts")). \
            filter(posts_count__gt=0). \
            order_by("-posts_count")[:8]

        other_tags = Tag.objects.exclude(id=self.tag.id).order_by("?")[:8]

        context.update({
            "tag": self.tag,
            "top_tags": top_tags,
            "other_tags": other_tags
        })

        return context


class UserPostListView(ListView):
    user = None
    model = Post
    context_object_name = "user_posts"
    template_name = "blog/user_post_list.html"
    paginate_by = 6

    def get_queryset(self):
        # Save user to use in other queries
        self.user = get_object_or_404(
            get_user_model(),
            username=self.kwargs["username"]
        )
        return self.user.posts. \
            select_related("user"). \
            prefetch_related("tags"). \
            filter(is_active=True). \
            order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        top_users = get_user_model().objects.annotate(posts_count=Count("posts")). \
            filter(posts_count__gt=0). \
            order_by("-posts_count")[:3]

        other_users = get_user_model().objects. \
            annotate(posts_count=Count("posts")). \
            filter(posts_count__gt=0). \
            exclude(username=self.user.username)[:3]

        context.update({
            "user": self.user,
            "top_users": top_users,
            "other_users": other_users
        })

        return context


class SearchPostListView(ListView):
    query = None
    model = Post
    context_object_name = "posts"
    template_name = "blog/search_post_list.html"
    paginate_by = 9

    def get_queryset(self):
        self.query = self.request.GET.get("q", "")
        if self.query:
            return Post.objects.select_related("user"). \
                prefetch_related("tags"). \
                filter(
                    Q(title__icontains=self.query) |
                    Q(user__first_name__icontains=self.query) |
                    Q(user__last_name__icontains=self.query) |
                    Q(tags__name__icontains=self.query),
                    is_active=True
                ). \
                order_by("-created_at").distinct()
        else:
            return Post.objects.select_related("user"). \
                prefetch_related("tags"). \
                filter(is_active=True). \
                order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.query
        return context


class MyPostListView(ListView):
    model = Post
    context_object_name = "posts"
    template_name = "blog/my_post_list.html"

    def get_queryset(self):
        posts = get_objects_for_user(
            user=self.request.user,
            perms="olp_blog_change_post",
            klass=Post
        )
        return posts.prefetch_related("tags").order_by("-created_at")


# @login_required(login_url="login")
# def bookmark_post(request, slug):
#     if request.method == "POST":
#         post = get_object_or_404(Post, slug=slug, is_active=True)
#         if post.bookmarks.filter(id=request.user.id).exists():
#             post.bookmarks.remove(request.user)
#         else:
#             post.bookmarks.add(request.user)
#     return redirect("post-detail", slug)


# @login_required(login_url="login")
# def bookmarked_posts(request):
#     posts = request.user.bookmarks.all(). \
#         filter(is_active=True). \
#         select_related("user"). \
#         prefetch_related("tags"). \
#         order_by("-created_at")

#     paginated_posts = paginate(request, queryset=posts)

#     context = {"posts": paginated_posts}
#     return render(request, "blog/bookmarked_posts.html", context)


# @login_required(login_url="login")
# def like_post(request, slug):
#     if request.method == "POST":
#         post = get_object_or_404(Post, slug=slug, is_active=True)
#         if post.likes.filter(id=request.user.id).exists():
#             post.likes.remove(request.user)
#         else:
#             post.likes.add(request.user)
#     return redirect("post-detail", slug)


# @login_required(login_url="login")
# def liked_posts(request):
#     posts = request.user.likes.all(). \
#         filter(is_active=True). \
#         select_related("user"). \
#         prefetch_related("tags"). \
#         order_by("-created_at")

#     paginated_posts = paginate(request, queryset=posts)

#     context = {"posts": paginated_posts}
#     return render(request, "blog/liked_posts.html", context)
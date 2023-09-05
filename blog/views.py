from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Q
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, DetailView, DeleteView
from django.views import View
from guardian.shortcuts import (
    assign_perm,
    get_objects_for_user,
    get_user_perms
)
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

        post = self.get_object()

        # Update post views
        post.views += 1
        post.save()

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


class PostCreateView(PermissionRequiredMixin, View):
    permission_required = "blog.add_post"

    def get(self, request):
        form = PostForm()
        context = {"form": form}
        return render(request, "blog/post_create_update.html", context)

    def post(self, request):
        form = PostForm(data=request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()

            # Save m2m relationships (tags)
            form.save_m2m()

            # Assign OLP permission to user
            assign_perm(
                perm="olp_blog_change_post",
                user_or_group=request.user,
                obj=post
            )

            messages.success(
                request,
                _("Post has been successfully created.")
            )
            return redirect("my-post-list")
        else:
            context = {"form": form}
            return render(request, "blog/post_create_update.html", context)


class PostUpdateView(PermissionRequiredMixin, View):
    permission_required = "blog.change_post"

    def get(self, request, slug):
        post = get_object_or_404(Post, slug=slug)

        if not request.user.has_perm(perm="olp_blog_change_post", obj=post):
            raise PermissionDenied()

        form = PostForm(instance=post)        
        context = {"form": form, "post": post}
        return render(request, "blog/post_create_update.html", context)

    def post(self, request, slug):
        post = get_object_or_404(Post, slug=slug)

        if not request.user.has_perm(perm="olp_blog_change_post", obj=post):
            raise PermissionDenied()

        form = PostForm(data=request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                message="Your post has been successfully edited."
            )
            return redirect("post-detail", post.slug)
        else:
            context = {"form": form}
            return render(request, "blog/post_create_update.html", context)


class PostDeleteView(PermissionRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Post
    success_url = reverse_lazy("my-post-list")
    permission_required = "blog.delete_post"
    success_message = "Your post has been successfully deleted."

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        if not self.request.user.has_perm(
            perm="olp_blog_change_post",
            obj=post
        ):
            raise PermissionDenied()


class TagPostListView(View):
    def get(self, request, tag_slug):
        tag = get_object_or_404(Tag, slug=tag_slug)

        tag_posts = tag.posts. \
            select_related("user"). \
            prefetch_related("tags"). \
            filter(is_active=True). \
            order_by("-created_at")

        top_tags = Tag.objects. \
            annotate(posts_count=Count("posts")). \
            filter(posts_count__gt=0). \
            order_by("-posts_count")[:8]
        
        other_tags = Tag.objects. \
            exclude(id=tag.id). \
            order_by("?")[:8]

        context = {
            "tag": tag,
            "tag_posts": tag_posts,
            "top_tags": top_tags,
            "other_tags": other_tags
        }
        return render(request, "blog/tag_post_list.html", context)


class UserPostListView(View):
    def get(self, request, username):
        user = get_object_or_404(get_user_model(), username=username)

        user_posts = user.posts. \
            select_related("user"). \
            prefetch_related("tags"). \
            filter(is_active=True). \
            order_by("-created_at")
        
        top_users = get_user_model().objects. \
            annotate(posts_count=Count("posts")). \
            filter(posts_count__gt=0). \
            order_by("-posts_count")[:3]

        other_users = get_user_model().objects. \
            annotate(posts_count=Count("posts")). \
            filter(posts_count__gt=0). \
            exclude(username=user.username)[:3]

        context = {
            "user": user,
            "user_posts": user_posts,
            "top_users": top_users,
            "other_users": other_users
        }
        return render(request, "blog/user_post_list.html", context)


class SearchPostsView(View):
    def get(self, request):
        query = request.GET.get("q", "")
        if query:
            posts = Post.objects. \
                select_related("user"). \
                prefetch_related("tags"). \
                filter(
                    Q(title__icontains=query) |
                    Q(user__first_name__icontains=query) |
                    Q(user__last_name__icontains=query) |
                    Q(tags__name__icontains=query),
                    is_active=True
                ). \
                order_by("-created_at").distinct()
        else:
            posts = Post.objects. \
                select_related("user"). \
                prefetch_related("tags"). \
                filter(is_active=True). \
                order_by("-created_at")

        context = {
            "query": query,
            "posts": posts
        }
        return render(request, "blog/search_posts.html", context)


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
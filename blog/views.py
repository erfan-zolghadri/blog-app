from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, F, Q
from django.forms.forms import BaseForm
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from guardian.shortcuts import (
    assign_perm,
    get_objects_for_user,
    get_user_perms
)

from accounts.mixins import UserAccessMixin
from blog.forms import CommentForm, PostForm
from blog.models import Comment, Post, Tag


class PostListView(ListView):
    model = Post
    context_object_name = "posts"
    template_name = "blog/post_list.html"
    paginate_by = 9

    def get_queryset(self):
        return Post.objects. \
            select_related("user"). \
            prefetch_related("tags"). \
            filter(status="published", is_active=True)


class PostDetailView(DetailView):
    model = Post
    context_object_name = "post"
    template_name = "blog/post_detail.html"

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        if (not post.is_active) or (post.status == Post.DRAFT):
            raise Http404()

        # Increment post's view
        post.views = F("views") + 1
        post.save()
        post.refresh_from_db()

        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        post = self.object
        post_tags = post.tags.all()
        post_perms = get_user_perms(user=self.request.user, obj=post)

        post_comments = post.comments.filter(is_active=True)
        post_comments_count = post_comments.count()

        form = CommentForm()

        related_posts = Post.objects.filter(
            status="published",
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
            "post_comments": post_comments,
            "post_comments_count": post_comments_count,
            "form": form,
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
    success_message = _("Your post has been successfully added.")
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
    permission_required = "blog.change_post"
    success_message = _("Your post has been successfully edited.")

    def dispatch(self, request, *args, **kwargs):
        """
        Check user has object-level permission (change) on post.
        """
        post = self.get_object()
        if not self.request.user.has_perm(
            perm="olp_blog_change_post", obj=post
        ):
            return redirect("accounts:dashboard")
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        if not post.is_active:
            raise Http404()
        return post

    def get_success_url(self):
        return reverse_lazy(
            viewname="blog:post-detail",
            kwargs={"slug": self.kwargs["slug"]}
        )


class PostDeleteView(UserAccessMixin, SuccessMessageMixin, DeleteView):
    model = Post
    success_url = reverse_lazy("blog:my-post-list")
    permission_required = "blog.delete_post"
    success_message = _("Your post has been successfully deleted.")

    def dispatch(self, request, *args, **kwargs):
        """
        Check user has object-level permission (change) on post.
        """
        post = self.get_object()
        if not self.request.user.has_perm(
            perm="olp_blog_change_post", obj=post
        ):
            return redirect("accounts:dashboard")
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        if not post.is_active:
            raise Http404()
        return post


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
            filter(status="published", is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        tag_posts_count = self.object_list.count()

        top_tags = Tag.objects.annotate(posts_count=Count("posts")). \
            filter(posts_count__gt=0). \
            order_by("-posts_count")[:8]

        other_tags = Tag.objects.exclude(id=self.tag.id).order_by("?")[:8]

        context.update({
            "tag": self.tag,
            "tag_posts_count": tag_posts_count,
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
            filter(status="published", is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_posts_count = self.object_list.count()

        top_users = get_user_model().objects. \
            annotate(posts_count=Count("posts")). \
            filter(posts_count__gt=0). \
            order_by("-posts_count")[:3]

        other_users = get_user_model().objects. \
            annotate(posts_count=Count("posts")). \
            filter(posts_count__gt=0). \
            exclude(username=self.user.username)[:3]

        context.update({
            "user": self.user,
            "user_posts_count": user_posts_count,
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
                    status="published",
                    is_active=True
                ).distinct()
        else:
            return Post.objects.select_related("user"). \
                prefetch_related("tags"). \
                filter(status="published", is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts_count = self.object_list.count()
        context.update({
            "query": self.query,
            "posts_count": posts_count
        })
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
        return posts.prefetch_related("tags").filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts_count = self.object_list.count()
        context["posts_count"] = posts_count
        return context


class CommentCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Comment
    form_class = CommentForm
    success_message = _("Thank you for your comment.")

    def form_valid(self, form: BaseForm):
        post = get_object_or_404(Post, slug=self.kwargs["slug"])
        comment = form.save(commit=False)
        comment.post = post
        comment.user = self.request.user
        comment.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            viewname="blog:post-detail",
            kwargs={"slug": self.kwargs["slug"]}
        )


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

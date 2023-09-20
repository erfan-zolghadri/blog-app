from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, F, Q
from django.forms.forms import BaseForm
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from guardian.shortcuts import (
    assign_perm,
    get_objects_for_user,
    get_user_perms
)

from accounts.mixins import UserAccessMixin
from blog.forms import CommentForm, PostForm
from blog.models import Category, Comment, Post, Tag


class CategoryPostListView(ListView):
    category = None
    model = Post
    context_object_name = 'posts'
    template_name = 'blog/category_post_list.html'
    paginate_by = 9

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Post.published.filter(category=self.category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class TagPostListView(ListView):
    tag = None
    model = Post
    context_object_name = 'tag_posts'
    template_name = 'blog/tag_post_list.html'
    paginate_by = 6

    def get_queryset(self):
        # Save tag to use in other queries
        self.tag = get_object_or_404(Tag, slug=self.kwargs['tag_slug'])

        return Post.published.filter(tags=self.tag)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        tag_posts_count = self.object_list.count()

        top_tags = Tag.get_top_tags(self)
        other_tags = Tag.objects.exclude(id=self.tag.id).order_by('?')[:8]

        context.update({
            'tag': self.tag,
            'tag_posts_count': tag_posts_count,
            'top_tags': top_tags,
            'other_tags': other_tags
        })

        return context


class UserPostListView(ListView):
    user = None
    model = Post
    context_object_name = 'user_posts'
    template_name = 'blog/user_post_list.html'
    # template_name = 'blog/test.html'
    paginate_by = 6

    def get_queryset(self):
        # Save user to use in other queries
        self.user = get_object_or_404(
            get_user_model(),
            username=self.kwargs['username']
        )

        return Post.published.filter(user=self.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_posts_count = self.object_list.count()

        # Top users based on the number of published posts
        published_posts_count = Count(
            'posts',
            filter=Q(posts__status=Post.POST_STATUS_PUBLISHED)
        )
        top_users = get_user_model().objects \
            .annotate(posts_count=published_posts_count) \
            .filter(posts_count__gt=0).order_by('-posts_count')[:3]

        other_users = get_user_model().objects. \
            annotate(posts_count=Count('posts')). \
            filter(posts_count__gt=0). \
            exclude(username=self.user.username)[:3]

        context.update({
            'user': self.user,
            'user_posts_count': user_posts_count,
            'top_users': top_users,
            'other_users': other_users
        })

        return context


class SearchPostListView(ListView):
    query = None
    model = Post
    context_object_name = 'posts'
    template_name = 'blog/search_post_list.html'
    paginate_by = 9

    def get_queryset(self):
        self.query = self.request.GET.get('q', '')
        if self.query:
            return Post.published.filter(
                Q(category__title__icontains=self.query) |
                Q(title__icontains=self.query) |
                Q(user__first_name__icontains=self.query) |
                Q(user__last_name__icontains=self.query) |
                Q(tags__name__icontains=self.query),
                is_active=True,
                status=Post.POST_STATUS_PUBLISHED
            ).distinct()
        else:
            return Post.published.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts_count = self.object_list.count()
        context.update({
            'query': self.query,
            'posts_count': posts_count
        })
        return context


class MyPostListView(UserAccessMixin, ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'blog/my_post_list.html'
    paginate_by = 9
    permission_required = 'blog.view_post'

    def get_queryset(self):
        posts = get_objects_for_user(
            user=self.request.user,
            perms='olp_blog_change_post',
            klass=Post
        )
        return posts.filter(is_active=True) \
            .select_related('user') \
            .prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts_count = self.object_list.count()
        context['posts_count'] = posts_count
        return context


class PostDetailView(DetailView):
    model = Post
    context_object_name = 'post'
    template_name = 'blog/post_detail.html'

    def get_object(self, queryset=None):
        post = super().get_object(queryset)

        if not post.is_active:
            raise Http404()

        # Allow only post authors to view their draft posts
        if (post.status == Post.POST_STATUS_DRAFT) and (post.user != self.request.user):
            raise Http404()

        # Increment post's view
        post.views = F('views') + 1
        post.save()
        post.refresh_from_db()

        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        post = self.object
        post_tags = post.tags.all()
        post_perms = get_user_perms(user=self.request.user, obj=post)

        post_comments = post.comments.filter(
            status=Comment.COMMENT_STATUS_APPROVED
        )
        post_comments_count = post_comments.count()

        # Check post is bookmarkable
        is_bookmarkable = True
        if post.status == Post.POST_STATUS_DRAFT:
            is_bookmarkable = False

        # Check current user has bookmarked post
        is_bookmarked = False
        if self.request.user in post.bookmarks.all():
            is_bookmarked = True

        form = CommentForm()

        related_posts = Post.published.filter(user=post.user) \
            .exclude(pk=post.pk)[:3]

        top_users = get_user_model().objects. \
            annotate(posts_count=Count('posts')). \
            filter(posts_count__gt=0) .\
            order_by('-posts_count')[:3]

        top_tags = Tag.get_top_tags(self)

        context.update({
            'post_tags': post_tags,
            'post_perms': post_perms,
            'is_bookmarkable': is_bookmarkable,
            'is_bookmarked': is_bookmarked,
            'post_comments': post_comments,
            'post_comments_count': post_comments_count,
            'form': form,
            'related_posts': related_posts,
            'top_users': top_users,
            'top_tags': top_tags
        })
        return context


class PostCreateView(UserAccessMixin, SuccessMessageMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_create_update.html'
    success_url = reverse_lazy('blog:my-post-list')
    success_message = _('Your post has been successfully added.')
    permission_required = 'blog.add_post'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.user = self.request.user
        post.save()

        # Save m2m relationship (tags)
        form.save_m2m()

        # Assign OLP permission to user
        assign_perm(
            perm='olp_blog_change_post',
            user_or_group=self.request.user,
            obj=post
        )

        return super().form_valid(form)


class PostUpdateView(UserAccessMixin, SuccessMessageMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_create_update.html'
    permission_required = 'blog.change_post'
    success_message = _('Your post has been successfully edited.')

    def dispatch(self, request, *args, **kwargs):
        '''
        Check user has object-level permission (change) on post.
        '''
        post = self.get_object()
        if not self.request.user.has_perm(
            perm='olp_blog_change_post', obj=post
        ):
            return redirect('accounts:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        if not post.is_active:
            raise Http404()
        return post

    def get_success_url(self):
        return reverse_lazy(
            viewname='blog:post-detail',
            kwargs={'slug': self.kwargs['slug']}
        )


class PostDeleteView(UserAccessMixin, SuccessMessageMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('blog:my-post-list')
    permission_required = 'blog.delete_post'
    success_message = _('Your post has been successfully deleted.')

    def dispatch(self, request, *args, **kwargs):
        '''
        Check user has object-level permission (change) on post.
        '''
        post = self.get_object()
        if not self.request.user.has_perm(
            perm='olp_blog_change_post', obj=post
        ):
            return redirect('accounts:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        if not post.is_active:
            raise Http404()
        return post


class CommentCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Comment
    form_class = CommentForm
    success_message = _('Thank you for your comment.')

    def form_valid(self, form: BaseForm):
        post = get_object_or_404(Post, slug=self.kwargs['slug'])
        comment = form.save(commit=False)
        comment.post = post
        comment.user = self.request.user
        comment.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            viewname='blog:post-detail',
            kwargs={'slug': self.kwargs['slug']}
        )


class BookmarkPostView(LoginRequiredMixin, View):
    def post(self, request):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            post_pk = int(request.POST.get('postPk'))
            post = get_object_or_404(
                Post,
                pk=post_pk,
                is_active=True,
                status=Post.POST_STATUS_PUBLISHED
            )

            if post.bookmarks.filter(id=request.user.id).exists():
                post.bookmarks.remove(request.user)
                status = 'success'
                message = 'bookmark removed'
            else:
                post.bookmarks.add(request.user)
                status = 'success'
                message = 'bookmarked'

            return JsonResponse({
                'status': status,
                'message': message
            })


class BookmarksView(LoginRequiredMixin, ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'blog/bookmarks.html'
    paginate_by = 9

    def get_queryset(self):
        return Post.published.filter(
            bookmarks=self.request.user
        )


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

from django.urls import path

from blog.views import (
    PostListView,
    CategoryPostListView,
    TagPostListView,
    UserPostListView,
    SearchPostListView,
    MyPostListView,
    PostDetailView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
    CommentCreateView
)

app_name = "blog"

urlpatterns = [
    path(
        "accounts/dashboard/posts/",
        MyPostListView.as_view(),
        name="my-post-list"
    ),
    path(
        "authors/<str:username>/",
        UserPostListView.as_view(),
        name="user-post-list"
    ),
    path(
        "categories/<slug:slug>/",
        CategoryPostListView.as_view(),
        name="category-post-list"
    ),
    path(
        "posts/search/",
        SearchPostListView.as_view(),
        name="search-post-list"
    ),
    path("posts/new/", PostCreateView.as_view(), name="post-create"),
    path("posts/<slug:slug>/", PostDetailView.as_view(), name="post-detail"),
    path(
        "posts/<slug:slug>/edit/",
        PostUpdateView.as_view(),
        name="post-update"
    ),
    path(
        "posts/<slug:slug>/delete/",
        PostDeleteView.as_view(),
        name="post-delete"
    ),
    path(
        "posts/<slug:slug>/comments/new/",
        CommentCreateView.as_view(),
        name="comment-create"
    ),
    path("posts/", PostListView.as_view(), name="post-list"),
    path(
        "tags/<slug:tag_slug>/",
        TagPostListView.as_view(),
        name="tag-post-list"
    )
]

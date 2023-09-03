from django.urls import path
from blog.views import (
    PostListView,
    PostDetailView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
    TagPostListView,
    UserPostListView,
    SearchPostsView,
    MyPostListView
)

urlpatterns = [
    path(
        "tags/<slug:tag_slug>/",
        TagPostListView.as_view(),
        name="tag_post_list"
    ),
    path(
        "authors/<str:username>/",
        UserPostListView.as_view(),
        name="user_post_list"
    ),
    path("posts/", PostListView.as_view(), name="post_list"),
    path("posts/search/", SearchPostsView.as_view(), name="search_posts"),
    path("posts/new/", PostCreateView.as_view(), name="post_create"),
    path("posts/<slug:slug>/", PostDetailView.as_view(), name="post_detail"),
    path("posts/<slug:slug>/edit/", PostUpdateView.as_view(), name="post_update"),
    path("posts/<slug:slug>/delete/", PostDeleteView.as_view(), name="post_delete"),
    path("my-posts/", MyPostListView.as_view(), name="my_post_list"),
]

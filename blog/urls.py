from django.urls import path

from blog import views

app_name = 'blog'

urlpatterns = [
    path(
        'bookmarks/',
        views.BookmarksView.as_view(),
        name='bookmarks'
    ),
    path(
        'my-posts/',
        views.MyPostListView.as_view(),
        name='my-post-list'
    ),
    path(
        'authors/<str:username>/',
        views.UserPostListView.as_view(),
        name='user-post-list'
    ),
    path(
        'categories/<slug:slug>/',
        views.CategoryPostListView.as_view(),
        name='category-post-list'
    ),
    path('posts/new/', views.PostCreateView.as_view(), name='post-create'),
    path(
        'posts/search/',
        views.SearchPostListView.as_view(),
        name='search-post-list'
    ),
    path(
        'posts/bookmark/',
        views.BookmarkPostView.as_view(),
        name='bookmark-post'
    ),
    path(
        'posts/<slug:slug>/comments/new/',
        views.CommentCreateView.as_view(),
        name='comment-create'
    ),
    path(
        'posts/<slug:slug>/delete/',
        views.PostDeleteView.as_view(),
        name='post-delete'
    ),
    path(
        'posts/<slug:slug>/edit/',
        views.PostUpdateView.as_view(),
        name='post-update'
    ),
    path(
        'posts/<slug:slug>/',
        views.PostDetailView.as_view(),
        name='post-detail'
    ),
    path(
        'tags/<slug:tag_slug>/',
        views.TagPostListView.as_view(),
        name='tag-post-list'
    ),
]

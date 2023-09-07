from django.views.generic.list import ListView

from blog.models import Post


class IndexView(ListView):
    model = Post
    context_object_name = "top_posts"
    template_name = "core/index.html"

    def get_queryset(self):
        return Post.objects.select_related("user"). \
            prefetch_related("tags"). \
            filter(is_active=True). \
            order_by("-views")[:3]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        recent_posts = Post.objects.select_related("user"). \
            prefetch_related("tags"). \
            filter(is_active=True). \
            order_by("-created_at")[:3]
        
        context["recent_posts"] = recent_posts
        return context

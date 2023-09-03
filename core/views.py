from django.shortcuts import render
from django.views.generic.base import TemplateView
from blog.models import Post


class Index(TemplateView):
    template_name = "core/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        top_posts = Post.objects. \
            select_related("user"). \
            prefetch_related("tags"). \
            filter(is_active=True). \
            order_by("-views")[:3]

        recent_posts = Post.objects. \
            select_related("user"). \
            prefetch_related("tags"). \
            filter(is_active=True). \
            order_by("-created_at")[:3]
        
        context.update({
            "top_posts": top_posts,
            "recent_posts": recent_posts
        })

        return context
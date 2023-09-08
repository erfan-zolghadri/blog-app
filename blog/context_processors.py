from blog.models import Category


def get_category_list(request):
    categories = Category.objects.all()
    context = {"categories": categories}
    return context

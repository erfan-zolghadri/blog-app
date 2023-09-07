from django import forms
from django.utils.translation import gettext_lazy as _

from blog.models import Post
from core.forms import BootstrapyForm


class PostForm(forms.ModelForm, BootstrapyForm):
    class Meta:
        model = Post
        fields = ["title", "content", "image", "status", "tags"]
from django import forms
from django.utils.translation import gettext_lazy as _

from blog.models import Comment, Post
from core.forms import BootstrapyForm


class CommentForm(forms.ModelForm, BootstrapyForm):
    class Meta:
        model = Comment
        fields = ["content"]

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields["content"].widget.attrs.update(
            {"placeholder": _("Write your comment")}
        )


class PostForm(forms.ModelForm, BootstrapyForm):
    class Meta:
        model = Post
        fields = ["title", "content", "image", "status", "tags"]

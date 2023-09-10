from django import forms
from django.utils.translation import gettext_lazy as _

from mptt.forms import TreeNodeChoiceField

from blog.models import Comment, Post
from core.forms import BootstrapyForm


class CommentForm(forms.ModelForm, BootstrapyForm):
    parent = TreeNodeChoiceField(queryset=Comment.objects.all())

    class Meta:
        model = Comment
        fields = ['parent', 'content']

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['parent'].required = False
        self.fields['content'].widget.attrs.update(
            {'placeholder': _('Write your comment')}
        )


class PostForm(forms.ModelForm, BootstrapyForm):
    class Meta:
        model = Post
        fields = ['category', 'title', 'content', 'image', 'status', 'tags']

from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')
        help_texts = {
            'text': ('в этом поле будет текст поста'),
            'group': ('в этом поле группа, в которой будет выложен пост')
        }

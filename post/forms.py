from tabnanny import verbose

from django import forms
from post.models import Post, Comment
from django.core.validators import MinLengthValidator, RegexValidator
from taggit.forms import TagField, TagWidget


class PostForm(forms.ModelForm):
    title = forms.CharField(required=True,
                            widget=forms.TextInput(
                                attrs={'class': 'form-control mt-1 mb-2'}
                            ),
                            validators=[MinLengthValidator(3, 'Title must be at least 3 characters')]
                            )

    content = forms.CharField(required=True,
                              widget=forms.Textarea(
                                  attrs={'class': 'form-control mt-1 mb-2', 'rows': 9}
                              ),
                              validators=[MinLengthValidator(10, 'Content must be at least 10 characters')]
                              )

    tags = TagField(
        required=False,
        widget=TagWidget(attrs={
            'class': 'form-control mt-1 mb-2',
            'placeholder': 'Enter tags separated by commas',
        }),
        validators=[MinLengthValidator(3, 'Tags must be at least 3 characters'),
                    RegexValidator(
                        regex=r'^[a-zA-Z]+(?:\s*,\s*[a-zA-Z]+)*$',
                        message='Tags must contain only English words separated by commas.')
                    ]
    )

    class Meta:
        model = Post
        fields = ['title', 'content', 'tags']


class CommentForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control mt-1', 'rows': 3}),
        validators=[
            MinLengthValidator(10, 'Comment must be at least 10 characters')
        ])

    class Meta:
        model = Comment
        fields = ['content']

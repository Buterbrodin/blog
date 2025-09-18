from django import forms

from post.models import Post


class PostForm(forms.ModelForm):
    title = forms.CharField(required=True, min_length=3, widget=forms.TextInput(attrs={'class': 'form-control mt-1'}))
    content = forms.CharField(required=True, widget=forms.Textarea(attrs={'class': 'form-control mt-1', 'rows': 9}),
                              min_length=10)

    class Meta:
        model = Post
        fields = ['title', 'content']

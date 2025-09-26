from tabnanny import verbose

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
from post.models import Post, Comment
from django.core.validators import MinLengthValidator, RegexValidator, EmailValidator
from django.contrib.auth.models import User
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
        label="Tags",
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


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control mt-1', 'placeholder': 'Username'}
        ),
        validators=[
            MinLengthValidator(4, 'Username must be at least 4 characters')
        ])
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control mt-1', 'placeholder': 'Password'}
        ),
        validators=[
            MinLengthValidator(8, 'Password must be at least 8 characters')
        ])

    class Meta:
        model = User
        fields = ['username', 'password']


class CustomRegisterForm(UserCreationForm):
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={
            "class": "form-control mt-1",
            "placeholder": "Username"
        }),
        validators=[
            MinLengthValidator(4, "Username must be at least 4 characters"),
            RegexValidator(r'^[a-zA-Z0-9_]+$', "Username can only contain letters, numbers and _")
        ]
    )

    email = forms.CharField(
        label="Email",
        widget=forms.TextInput(attrs={
            "class": "form-control mt-1",
            "placeholder": "Email"
        }),
        validators=[EmailValidator('Invalid email format.')],
        required=True
    )

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control mt-1",
            "placeholder": "Password"
        }),
        validators=[
            MinLengthValidator(8, "Password must be at least 8 characters")
        ]
    )

    password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control mt-1",
            "placeholder": "Confirm Password"
        }),
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        error_messages = {
            "password2": {"password_mismatch": "Passwords don't match, please try again"}
        }


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label='Current password',
        widget=forms.PasswordInput(attrs={'class': 'form-control mb-2'})
    )
    new_password1 = forms.CharField(
        label='New password',
        widget=forms.PasswordInput(attrs={'class': 'form-control mb-2'})
    )
    new_password2 = forms.CharField(
        label='Confirm new password',
        widget=forms.PasswordInput(attrs={'class': 'form-control mb-2'})
    )

    class Meta:
        fields = ("old_password", "new_password1", "new_password2")

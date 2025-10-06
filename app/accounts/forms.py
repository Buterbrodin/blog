from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm, PasswordResetForm, \
    SetPasswordForm
from django.core.validators import MinLengthValidator, RegexValidator, EmailValidator
from django.contrib.auth.models import User
from accounts.models import Profile
from django_recaptcha.fields import ReCaptchaField


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
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                'class': 'form-check-input ms-1',
                'style': 'margin-top: 6px',
            }
        )
    )

    recaptcha = ReCaptchaField(label="")

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

    recaptcha = ReCaptchaField(label="")

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


class UserForm(forms.ModelForm):
    username = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control mt-1'
            }
        ),
        validators=[MinLengthValidator(4, "Username must be at least 4 characters"), ]
    )
    email = forms.EmailField(
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control mt-1'
            }
        )
    )

    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileForm(forms.ModelForm):
    avatar = forms.ImageField(
        widget=forms.FileInput(
            attrs={
                'class': 'form-control mt-1',
            }
        ))
    bio = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'form-control mt-1',
                'rows': 5
            }
        ), required=False
    )

    class Meta:
        model = Profile
        fields = ['avatar', 'bio']


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control mt-1'
            }
        ))
    recaptcha = ReCaptchaField(label="")


class CustomPasswordResetConfirmForm(SetPasswordForm):
    new_password1 = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'form-control mt-1',
        }
    ),
        label='New password',
        validators=[
            MinLengthValidator(8, "Password must be at least 8 characters")
        ]
    )
    new_password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'form-control mt-1',
        }
    ),
        label='Confirm new password',
    )

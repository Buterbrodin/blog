from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordResetView, \
    PasswordResetConfirmView
from django.views.generic.edit import CreateView
from django.views.generic import DetailView
from django.urls import reverse_lazy
from django.shortcuts import render
from django.contrib.auth import login
from django.shortcuts import redirect
from django.contrib import messages
from accounts.forms import CustomLoginForm, CustomRegisterForm, CustomPasswordChangeForm, ProfileForm, UserForm, \
    CustomPasswordResetForm, CustomPasswordResetConfirmForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from accounts.tokens import account_activation_token
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str


class CustomLoginView(UserPassesTestMixin, LoginView):
    '''Custom login view'''
    authentication_form = CustomLoginForm
    template_name = 'registration/login.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        messages.success(self.request, 'You are now logged in!')
        remember_me = form.cleaned_data.get('remember_me')
        if not remember_me:
            self.request.session.set_expiry(0)
            self.request.session.modified = True
        return super().form_valid(form)

    def form_invalid(self, form):
        user = User.objects.filter(username=form.cleaned_data.get('username')).first()
        if user and not user.is_active:
            messages.error(self.request, 'Your account is not active! Please check your email for confirmation.')
            return redirect('login')
        return super().form_invalid(form)

    def test_func(self):
        return self.request.user.is_anonymous

    def handle_no_permission(self):
        messages.error(self.request, 'You are already logged in!')
        return redirect('home')


class CustomRegisterView(UserPassesTestMixin, CreateView):
    '''Custom register view'''
    form_class = CustomRegisterForm
    template_name = "registration/register.html"
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        messages.info(self.request,
                      'You have successfully registered a new account! Please check your email for confirmation.')
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        return redirect('home')

    def test_func(self):
        return self.request.user.is_anonymous

    def handle_no_permission(self):
        messages.error(self.request, 'You are already logged in!')
        return redirect('home')


class CustomLogoutView(LogoutView):
    '''Custom logout view'''

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "You have been logged out!")
        return super().dispatch(request, *args, **kwargs)


class CustomPasswordChangeView(PasswordChangeView):
    '''Custom password change view'''
    form_class = CustomPasswordChangeForm
    template_name = 'registration/password_change.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        messages.success(self.request, 'You have successfully changed the password!')
        return super().form_valid(form)


class CustomPasswordRestView(PasswordResetView):
    template_name = 'registration/password_reset.html'
    form_class = CustomPasswordResetForm
    email_template_name = 'registration/password_reset_email.txt'
    email_subject_template_name = 'registration/password_reset_subject.txt'

    def get_success_url(self):
        messages.success(self.request, 'Check your email for instructions to reset your password.')
        return reverse_lazy('home')


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    form_class = CustomPasswordResetConfirmForm

    def get_success_url(self):
        messages.success(self.request, 'You have successfully reset your password!')
        return reverse_lazy('home')


@login_required
def profile(request):
    user_form = UserForm(instance=request.user)
    profile_form = ProfileForm(instance=request.user.profile)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'You have successfully changed your profile!')
            return redirect('profile')
    return render(request, 'accounts/profile.html',
                  {'user_form': user_form, 'profile_form': profile_form})


def activate(request, uuid64, token):
    try:
        uuid = force_str(urlsafe_base64_decode(uuid64))
        user = User.objects.get(pk=uuid)
    except (ValueError, User.DoesNotExist):
        user = None

    if user and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'You have successfully activated your account!')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link or account is already activated!')
        return redirect('login')

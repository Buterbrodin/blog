from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.views.generic.edit import CreateView
from django.views.generic import DetailView
from django.urls import reverse_lazy
from django.shortcuts import render
from django.contrib.auth import login
from django.shortcuts import redirect
from django.contrib import messages
from accounts.forms import CustomLoginForm, CustomRegisterForm, CustomPasswordChangeForm, ProfileForm, UserForm
from django.contrib.auth.decorators import login_required

status = {'info': 'primary', 'success': 'success', 'error': 'danger'}
icons = {'info': 'bi-info-circle',
         'success': 'bi-check-circle',
         'error': 'bi-exclamation-triangle'}


class CustomLoginView(LoginView):
    '''Custom login view'''
    authentication_form = CustomLoginForm
    template_name = 'registration/login.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        messages.success(self.request, 'You are now logged in!')
        return super().form_valid(form)


class CustomRegisterView(CreateView):
    '''Custom register view'''
    form_class = CustomRegisterForm
    template_name = "registration/register.html"
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        messages.success(self.request, 'You have successfully registered a new account!')
        user = form.save()
        login(self.request, user)
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
                  {'user_form': user_form, 'profile_form': profile_form, 'status': status, 'icons': icons})

from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordResetView, \
    PasswordResetConfirmView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import messages
from accounts.forms import CustomLoginForm, CustomRegisterForm, CustomPasswordChangeForm, ProfileForm, UserForm, \
    CustomPasswordResetForm, CustomPasswordResetConfirmForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from accounts.tokens import account_activation_token
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.mixins import LoginRequiredMixin


class CustomLoginView(UserPassesTestMixin, LoginView):
    """
    Custom login view.

    Features:
        * Uses custom login form.
        * Only anonymous users can get access.
        * If user is already authenticated, redirects to home page, adds an error message.
        * In case user is not verified via email message, redirects to login page and adds an error message.
        * If user is successfully authenticated, redirects to home page, adds a successful message.
    """
    authentication_form = CustomLoginForm
    template_name = 'registration/login.html'

    def get_success_url(self):
        """After a successful authentication, redirects to home page."""
        return reverse_lazy('home')

    def form_valid(self, form):
        """
        * If form is valid, adds a successful message.
        * If remember me is not checked sets the session expiry to 0
        """
        messages.success(self.request, 'You are now logged in!')
        remember_me = form.cleaned_data.get('remember_me')
        if not remember_me:
            self.request.session.set_expiry(0)
            self.request.session.modified = True
        return super().form_valid(form)

    def form_invalid(self, form):
        """If for is not valid, checks if user is not verified via email message, redirects to login page and adds an error message."""
        user = User.objects.filter(username=form.cleaned_data.get('username')).first()
        if user and not user.is_active:
            messages.error(self.request, 'Your account is not active! Please check your email for confirmation.')
            return redirect('login')
        return super().form_invalid(form)

    def test_func(self):
        """Provides access to the CustomLoginView only to anonymous users."""
        return self.request.user.is_anonymous

    def handle_no_permission(self):
        """If user is already logged in, redirects to home page and adds an error message."""
        messages.error(self.request, 'You are already logged in!')
        return redirect('home')


class CustomRegisterView(UserPassesTestMixin, CreateView):
    '''
    Custom register view

    Features:
      * Uses a custom register form
      * Only anonymous users can get access
      * If an authenticated user tries to access the register page, redirects to home page and adds an error message
      * If form is valid adds a successful message and redirects to home page
      * Creates a user with is_active=False to verify users via email
    '''
    form_class = CustomRegisterForm
    template_name = "registration/register.html"
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        """If form is valid creates a user with is_active=False and adds a successful message and redirects to home page"""
        messages.info(self.request,
                      'You have successfully registered a new account! Please check your email for confirmation.')
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        return redirect('home')

    def test_func(self):
        """Provides access to the CustomRegisterView only to anonymous users."""
        return self.request.user.is_anonymous

    def handle_no_permission(self):
        """If user is already logged in, redirects to home page and adds an error message."""
        messages.error(self.request, 'You are already logged in!')
        return redirect('home')


class CustomLogoutView(UserPassesTestMixin, LogoutView):
    """
    Custom logout view

    Features:
      * Uses a custom logout form
      * Only authenticated users can get access
      * If an anonymous user tries to access the logout page, redirects to login page and adds an error message
      * If user is successfully logged out, redirects to home page and adds a successful message
      * If user is not authenticated, redirects to login page and adds an error message
    """

    def post(self, request, *args, **kwargs):
        """If user is successfully logged out, redirects to home page and adds a successful message"""
        messages.success(request, "You have been logged out!")
        return super().post(request, *args, **kwargs)

    def test_func(self):
        """Provides access to the CustomLogoutView only to authenticated users."""
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        """If user is not authenticated, redirects to login page and adds an error message."""
        messages.error(self.request, 'You are not logged in!')
        return redirect('login')


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """
    CustomPasswordChangeView

    Features:
      * Uses a custom password change form
      * Only authenticated users can get access
      * If an anonymous user tries to access the password change page, redirects to login page and adds an error message
      * If password is successfully changed, redirects to home page and adds a successful message
    """
    form_class = CustomPasswordChangeForm
    template_name = 'registration/password_change.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        """If password is successfully changed, redirects to home page and adds a successful message"""
        messages.success(self.request, 'You have successfully changed the password!')
        return super().form_valid(form)

    def handle_no_permission(self):
        """If user is not authenticated, redirects to login page and adds an error message."""
        messages.error(self.request, 'You are not authenticated!')
        return super().handle_no_permission()


class CustomPasswordResetView(UserPassesTestMixin, PasswordResetView):
    """
    CustomPasswordResetView

    Features:
      * Uses a custom password reset form
      * Only anonymous users can get access
      * If an authenticated user tries to access the password reset page, redirects to home page and adds an error message
      * If password reset is successfully sent, redirects to home page and adds a successful message
      * Uses a custom email template
      * Uses a custom email subject template
    """
    template_name = 'registration/password_reset.html'
    form_class = CustomPasswordResetForm
    email_template_name = 'registration/password_reset_email.txt'
    email_subject_template_name = 'registration/password_reset_subject.txt'

    def get_success_url(self):
        """If password reset message is successfully sent, redirects to home page and adds a successful message."""
        messages.success(self.request, 'Check your email for instructions to reset your password.')
        return reverse_lazy('home')

    def test_func(self):
        """Provides access to the CustomPasswordResetView only to anonymous users."""
        return self.request.user.is_anonymous

    def handle_no_permission(self):
        """If user is authenticated, redirects to home page and adds an error message."""
        messages.error(self.request, 'You are authorized! Use the password change button.')
        return redirect('home')


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """
    CustomPasswordResetConfirmView

    Features:
      * Uses a custom password reset confirm form
      * If form is valid redirects to home page and adds a successful message
    """
    template_name = 'registration/password_reset_confirm.html'
    form_class = CustomPasswordResetConfirmForm

    def get_success_url(self):
        """If form is valid redirects to home page and adds a successful message."""
        messages.success(self.request, 'You have successfully reset your password!')
        return reverse_lazy('home')


@login_required
def profile(request):
    """
    Profile view

    Features:
      * Uses a custom profile form
      * Creates user profile after user registration
      * If form is valid redirects to profile page and adds a successful message
    """
    user_form = UserForm(instance=request.user)
    profile_form = ProfileForm(instance=request.user.profile)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)  # fills the user form with data from the request
        profile_form = ProfileForm(request.POST, request.FILES,
                                   instance=request.user.profile)  # fills the profile form with data from the request
        if user_form.is_valid() and profile_form.is_valid():  # if forms are valid saves them
            user_form.save()  # saves the user form
            profile_form.save()  # saves the profile form
            messages.success(request, 'You have successfully changed your profile!')  # adds a successful message
            return redirect('profile')  # redirects to profile page
    return render(request, 'accounts/profile.html',
                  {'user_form': user_form, 'profile_form': profile_form})


def activate(request, uuid64, token):
    """
    Activate view

    Features:
      * Activates user account
      * Uses a token
      * Uses coded pk of a user instance
      * If user is not found redirects to login page and adds an error message
      * If user is already activated redirects to login page and adds an error message
      * If user is successfully activated redirects to login page and adds a successful message
    """
    try:
        uuid = force_str(urlsafe_base64_decode(uuid64))  # decodes the uuid64 from the link
        user = User.objects.get(pk=uuid)  # gets the user from the database
    except (ValueError, User.DoesNotExist):  # if user is not found
        user = None  # sets user to None

    if user and account_activation_token.check_token(user, token):  # if user is found and the token is valid
        user.is_active = True  # sets user.is_active to True
        user.save()  # saves the user
        messages.success(request, 'You have successfully activated your account!')  # adds a successful message
        return redirect('login')  # redirects to login page
    else:
        messages.error(request, 'Invalid activation link or account is already activated!')  # adds an error message
        return redirect('login')  # redirects to login page

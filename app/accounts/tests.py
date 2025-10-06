from django.test import TestCase
from django.contrib.auth.models import User
from accounts.models import Profile
from django.urls import reverse, resolve
from app import accounts as views
import accounts as forms
from accounts.tokens import account_activation_token
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


class AccountsFormTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='TestUser', is_active=True)
        self.user.set_password('Assembler7002')
        self.user.save()

    def test_custom_login_form_valid(self):
        form_data = {'username': 'TestUser', 'password': 'Assembler7002', 'remember_me': True}
        form = forms.CustomLoginForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_custom_login_form_invalid(self):
        form_data = {'username': 'inv', 'password': 'inv', 'remember_me': True}
        form = forms.CustomLoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertFormError(form, 'username', 'Username must be at least 4 characters')
        self.assertFormError(form, 'password', 'Password must be at least 8 characters')

    def test_custom_login_form_empty(self):
        form_data = {'username': '', 'password': '', 'remember_me': True}
        form = forms.CustomLoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertFormError(form, 'username', 'This field is required.')
        self.assertFormError(form, 'username', 'This field is required.')

    def test_custom_register_form_valid(self):
        form_data = {'username': 'valid_username', 'email': 'valid@email.com', 'password1': 'Assembler7002',
                     'password2': 'Assembler7002'}
        form = forms.CustomRegisterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_custom_register_form_invalid(self):
        form_data = {'username': 'inv', 'email': 'inv', 'password1': 'inv',
                     'password2': 'inv'}
        form = forms.CustomRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertFormError(form, 'username', 'Username must be at least 4 characters')
        self.assertFormError(form, 'email', 'Invalid email format.')
        self.assertFormError(form, 'password1', 'Password must be at least 8 characters')

    def test_custom_register_form_empty(self):
        form_data = {'username': '', 'email': '', 'password1': '', 'password2': ''}
        form = forms.CustomRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertFormError(form, 'username', 'This field is required.')
        self.assertFormError(form, 'email', 'This field is required.')
        self.assertFormError(form, 'password1', 'This field is required.')
        self.assertFormError(form, 'password2', 'This field is required.')

    def test_custom_password_change_form_valid(self):
        form_data = {'old_password': 'Assembler7002', 'new_password1': 'Assembler7003',
                     'new_password2': 'Assembler7003'}
        form = forms.CustomPasswordChangeForm(self.user, data=form_data)
        self.assertTrue(form.is_valid())

    def test_custom_password_change_form_old_password_invalid(self):
        form_data = {'old_password': 'inv', 'new_password1': 'Assembler7003',
                     'new_password2': 'Assembler7003'}
        form = forms.CustomPasswordChangeForm(self.user, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertFormError(form, 'old_password', 'Your old password was entered incorrectly. Please enter it again.')

    def test_custom_password_change_form_old_password_valid_new_password_invalid(self):
        form_data = {'old_password': 'Assembler7002', 'new_password1': 'inv',
                     'new_password2': 'inv'}
        form = forms.CustomPasswordChangeForm(self.user, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertFormError(form, 'new_password2',
                             'This password is too short. It must contain at least 8 characters.')

    def test_custom_password_change_form_old_password_valid_new_password_dont_match(self):
        form_data = {'old_password': 'Assembler7002', 'new_password1': 'Assembler7003',
                     'new_password2': 'Assembler7004'}
        form = forms.CustomPasswordChangeForm(self.user, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertFormError(form, 'new_password2',
                             'The two password fields didn’t match.')

    def test_user_form_valid(self):
        form_data = {'username': 'TestUser2', 'email': 'test@email.com'}
        form = forms.UserForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_user_form_invalid(self):
        form_data = {'username': 'inv', 'email': 'inv'}
        form = forms.UserForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertFormError(form, 'username', 'Username must be at least 4 characters')
        self.assertFormError(form, 'email', 'Enter a valid email address.')

    def test_user_form_empty(self):
        form_data = {'username': '', 'email': ''}
        form = forms.UserForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertFormError(form, 'username', 'This field is required.')
        self.assertFormError(form, 'email', 'This field is required.')

    def test_profile_form_empty(self):
        form_data = {'avatar': '', 'bio': ''}
        form = forms.ProfileForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_test_custom_password_reset_form_valid(self):
        form_data = {'email': 'test@email.com'}
        form = forms.CustomPasswordResetForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_test_custom_password_reset_form_invalid(self):
        form_data = {'email': 'inv'}
        form = forms.CustomPasswordResetForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertFormError(form, 'email', 'Enter a valid email address.')

    def test_test_custom_password_reset_form_empty(self):
        form_data = {'email': ''}
        form = forms.CustomPasswordResetForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertFormError(form, 'email', 'This field is required.')

    def test_custom_password_reset_confirm_form_valid(self):
        form_data = {'new_password1': 'Assembler7003', 'new_password2': 'Assembler7003'}
        form = forms.CustomPasswordResetConfirmForm(self.user, data=form_data)
        self.assertTrue(form.is_valid())

    def test_custom_password_reset_confirm_form_invalid(self):
        form_data = {'new_password1': 'inv', 'new_password2': 'inv'}
        form = forms.CustomPasswordResetConfirmForm(self.user, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertFormError(form, 'new_password1',
                             'Password must be at least 8 characters')

    def test_custom_password_reset_confirm_form_dont_match(self):
        form_data = {'new_password1': 'Assembler7003', 'new_password2': 'Assembler7004'}
        form = forms.CustomPasswordResetConfirmForm(self.user, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertFormError(form, 'new_password2', 'The two password fields didn’t match.')

    def test_custom_password_reset_confirm_form_empty(self):
        form_data = {'new_password1': '', 'new_password2': ''}
        form = forms.CustomPasswordResetConfirmForm(self.user, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertFormError(form, 'new_password1', 'This field is required.')
        self.assertFormError(form, 'new_password2', 'This field is required.')


class AccountURLsAndTemplatesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='TestUser', is_active=True)
        self.user.set_password('Assembler7002')
        self.user.save()

    def test_login_url_view(self):
        url = reverse('login')
        match = resolve(url)
        self.assertEqual(match.func.view_class, views.CustomLoginView)

    def test_login_url_response(self):
        url = reverse('login')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_oauth_url_redirect(self):
        url = reverse('oauth:begin', args=['github'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_logout_url_view(self):
        url = reverse('logout')
        match = resolve(url)
        self.assertEqual(match.func.view_class, views.CustomLogoutView)

    def test_logout_redirect_authenticated(self):
        self.client.login(username=self.user.username, password="Assembler7002")
        url = reverse("logout")
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("home"))
        self.assertTemplateUsed(response, 'post/home.html')
        self.assertContains(response, 'You have been logged out!')

    def test_logout_redirect_not_authenticated(self):
        url = reverse("logout")
        response = self.client.post(url, follow=True)
        self.assertRedirects(response, reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_register_url_view(self):
        url = reverse('register')
        match = resolve(url)
        self.assertEqual(match.func.view_class, views.CustomRegisterView)

    def test_register_url_response(self):
        url = reverse('register')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')

    def test_register_url_create_user(self):
        url = reverse('register')
        context = {'username': 'TestUser2', 'email': 'test@user.com', 'password1': 'Testpassword123',
                   'password2': 'Testpassword123'}
        response = self.client.post(url, context, follow=True)
        new_user = User.objects.get(username='TestUser2')
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('home'))
        self.assertTemplateUsed(response, 'post/home.html')
        self.assertEqual(User.objects.count(), 2)  # +1 user from setUp
        self.assertFalse(new_user.is_active)

    def test_register_url_create_user_invalid(self):
        url = reverse('register')
        context = {'username': '', 'email': '', 'password1': '', 'password2': ''}
        response = self.client.post(url, context)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 1)  # user from setUp
        self.assertTemplateUsed(response, 'registration/register.html')

    def test_password_change_url_view(self):
        url = reverse('password_change')
        match = resolve(url)
        self.assertEqual(match.func.view_class, views.CustomPasswordChangeView)

    def test_password_change_url_response_not_authenticated(self):
        url = reverse('password_change')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, f'{reverse('login')}?next={url}')
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_password_change_url_response_authenticated(self):
        self.client.login(username=self.user.username, password='Assembler7002')
        url = reverse('password_change')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/password_change.html')
        self.assertIn('form', response.context)

    def test_password_change_url_valid(self):
        url = reverse('password_change')
        self.client.login(username=self.user.username, password='Assembler7002')
        context = {'old_password': 'Assembler7002', 'new_password1': 'Assembler7003', 'new_password2': 'Assembler7003'}
        response = self.client.post(url, context, follow=True)
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(username=self.user.username)
        self.assertTrue(user.check_password('Assembler7003'))
        self.assertTemplateUsed(response, 'post/home.html')
        self.assertContains(response, 'You have successfully changed the password!')

    def test_password_change_url_invalid(self):
        url = reverse('password_change')
        self.client.login(username=self.user.username, password='Assembler7002')
        context = {'old_password': '', 'new_password1': '', 'new_password2': ''}
        response = self.client.post(url, context, follow=True)
        user = User.objects.get(username=self.user.username)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(user.check_password(''))
        self.assertTemplateUsed(response, 'registration/password_change.html')

    def test_profile_url_view(self):
        url = reverse('profile')
        match = resolve(url)
        self.assertEqual(match.func, views.profile)

    def test_profile_url_response_not_authenticated(self):
        url = reverse('profile')
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, f'{reverse('login')}?next={url}')
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_profile_url_response_authenticated(self):
        url = reverse('profile')
        self.client.login(username=self.user.username, password='Assembler7002')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')

    def test_profile_url_edit(self):
        url = reverse('profile')
        self.client.login(username=self.user.username, password='Assembler7002')
        context = {'bio': 'test bio', 'username': 'TestUserEdited', 'email': 'edited@gmail.com'}
        response = self.client.post(url, context, follow=True)
        user = User.objects.get(username='TestUserEdited')
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('profile'))
        self.assertTemplateUsed(response, 'accounts/profile.html')
        self.assertEqual(user.profile.bio, 'test bio')
        self.assertEqual(user.username, 'TestUserEdited')
        self.assertEqual(user.email, 'edited@gmail.com')

    def test_profile_url_edit_invalid(self):
        url = reverse('profile')
        self.client.login(username=self.user.username, password='Assembler7002')
        context = {'bio': '', 'username': '', 'email': '', 'avatar': ''}
        response = self.client.post(url, context, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')
        self.assertFalse(User.objects.filter(username='').exists())

    def test_activate_url_view(self):
        url = reverse('activate', args=['first', 'second'])
        match = resolve(url)
        self.assertEqual(match.func, views.activate)

    def test_activate_url_valid(self):
        user = User.objects.create(username='user-activate', is_active=False)
        user.set_password('Assember7002')
        user.save()
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)
        url = reverse('activate', args=[uid, token])
        response = self.client.get(url, follow=True)
        user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('login'))
        self.assertTemplateUsed(response, 'registration/login.html')
        self.assertTrue(user.is_active)

    def test_activate_url_invalid(self):
        user = User.objects.create(username='user-activate-invalid', is_active=False)
        user.set_password('Assember7002')
        user.save()
        url = reverse('activate', args=['invalid', 'invalid'])
        response = self.client.get(url, follow=True)
        user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('login'))
        self.assertTemplateUsed(response, 'registration/login.html')
        self.assertFalse(user.is_active)
        self.assertContains(response, 'Invalid activation link')

    def test_password_change_url_view(self):
        url = reverse('password_change')
        match = resolve(url)
        self.assertEqual(match.func.view_class, views.CustomPasswordChangeView)

    def test_password_change_url_response_not_authenticated(self):
        url = reverse('password_change')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, f"{reverse('login')}?next={url}")
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_password_change_url_response_not_authenticated(self):
        url = reverse('password_change')
        self.client.login(username=self.user.username, password='Assembler7002')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/password_change.html')

    def test_password_change_url_response_valid(self):
        url = reverse('password_change')
        self.client.login(username=self.user.username, password='Assembler7002')
        context = {'old_password': 'Assembler7002', 'new_password1': 'Assembler7003', 'new_password2': 'Assembler7003'}
        response = self.client.post(url, context, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('home'))
        self.assertTemplateUsed(response, 'post/home.html')
        user = User.objects.get(username=self.user.username)
        self.assertTrue(user.check_password('Assembler7003'))

    def test_password_change_url_response_invalid(self):
        url = reverse('password_change')
        self.client.login(username=self.user.username, password='Assembler7002')
        context = {'old_password': '', 'new_password1': '', 'new_password2': ''}
        response = self.client.post(url, context, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/password_change.html')
        user = User.objects.get(username=self.user.username)
        self.assertFalse(user.check_password(''))

    def test_password_reset_url_view(self):
        url = reverse('password_reset')
        match = resolve(url)
        self.assertEqual(match.func.view_class, views.CustomPasswordResetView)

    def test_password_reset_url_response(self):
        url = reverse('password_reset')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/password_reset.html')

    def test_password_reset_url_valid(self):
        url = reverse('password_reset')
        response = self.client.post(url, {'email': 'test@gmail.com'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('home'))
        self.assertTemplateUsed(response, 'post/home.html')
        self.assertContains(response, 'Check your email for instructions')

    def test_password_reset_url_invalid(self):
        url = reverse('password_reset')
        response = self.client.post(url, {'email': ''}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/password_reset.html')
        self.assertFormError(response.context['form'], 'email', 'This field is required.')


class AccountModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='test-login')
        self.profile = Profile.objects.get(user=self.user)

    def test_profile_creation(self):
        self.assertIsInstance(self.profile, Profile)
        self.assertEqual(self.profile.avatar.name, 'default.png')

    def test_profile_str(self):
        self.assertEqual(str(self.profile), 'test-login')

    def test_profile_save(self):
        user1 = User.objects.create(username='test-login1')
        user2 = User.objects.create(username='test-login2')

        user1.profile.bio = 'test bio 1'
        user2.profile.bio = 'test bio 2'
        user1.profile.save()
        user2.profile.save()

        profiles = Profile.objects.all()
        self.assertEqual(profiles.count(), 3)
        self.assertEqual(user1.profile.bio, 'test bio 1')
        self.assertEqual(user2.profile.bio, 'test bio 2')

    def test_profile_avatar(self):
        self.profile.avatar = 'test-avatar.png'
        self.assertEqual(self.profile.avatar, 'test-avatar.png')

    def test_profile_unique(self):
        with self.assertRaises(Exception):
            Profile.objects.create(user=self.user, bio='duplicate')

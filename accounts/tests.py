from django.contrib.auth.tokens import default_token_generator
from django.test import TestCase
from django.contrib.auth.models import User
from accounts.models import Profile
from django.urls import reverse, resolve
import accounts.views as views
from accounts.tokens import account_activation_token
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator


class AccountURLsTests(TestCase):
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
        self.assertRedirects(response, reverse("home"))

    def test_logout_redirect_not_authenticated(self):
        url = reverse("logout")
        response = self.client.post(url, follow=True)
        self.assertRedirects(response, reverse('login'))
        self.assertEqual(response.status_code, 200)

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
        self.assertEqual(User.objects.count(), 2)  # +1 user from setUp
        self.assertFalse(new_user.is_active)

    def test_register_url_create_user_invalid(self):
        url = reverse('register')
        context = {'username': '', 'email': '', 'password1': '', 'password2': ''}
        response = self.client.post(url, context)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 1)  # user from setUp

    def test_password_change_url_view(self):
        url = reverse('password_change')
        match = resolve(url)
        self.assertEqual(match.func.view_class, views.CustomPasswordChangeView)

    def test_password_change_url_response_not_authenticated(self):
        url = reverse('password_change')
        response = self.client.get(url)
        self.assertRedirects(response, f'{reverse('login')}?next={url}')

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
        response = self.client.get(url)
        self.assertRedirects(response, f'{reverse('login')}?next={url}')

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
        self.assertRedirects(response, reverse('profile'))
        self.assertEqual(response.status_code, 200)
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
        self.assertFalse(user.is_active)
        self.assertContains(response, 'Invalid activation link')

    def test_password_change_url_view(self):
        url = reverse('password_change')
        match = resolve(url)
        self.assertEqual(match.func.view_class, views.CustomPasswordChangeView)

    def test_password_change_url_response_not_authenticated(self):
        url = reverse('password_change')
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, f"{reverse('login')}?next={url}")
        self.assertEqual(response.status_code, 200)

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
        user = User.objects.get(username=self.user.username)
        self.assertTrue(user.check_password('Assembler7003'))

    def test_password_change_url_response_invalid(self):
        url = reverse('password_change')
        self.client.login(username=self.user.username, password='Assembler7002')
        context = {'old_password': '', 'new_password1': '', 'new_password2': ''}
        response = self.client.post(url, context, follow=True)
        self.assertEqual(response.status_code, 200)
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
        self.assertContains(response, 'Check your email for instructions')

    def test_password_reset_url_invalid(self):
        url = reverse('password_reset')
        response = self.client.post(url, {'email': ''}, follow=True)
        self.assertEqual(response.status_code, 200)
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

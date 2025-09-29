from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from accounts.models import Profile
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.conf import settings
from accounts.tokens import account_activation_token


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def send_email(sender, instance, created, **kwargs):
    if created and not instance.is_active:
        uid = urlsafe_base64_encode(force_bytes(instance.pk))
        token = account_activation_token.make_token(instance)

        activation_link = f'http://127.0.0.1:8000/accounts/activate/{uid}/{token}/'

        send_mail(
            'Verificate your account',
            'Please click on the link to verificate your account: ' + activation_link,
            settings.EMAIL_HOST_USER,
            [instance.email],
            fail_silently=False,
        )

from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from accounts.models import Profile
from accounts.tasks import send_email


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def user_update(sender, instance, created, **kwargs):
    if created and not instance.is_active:
        send_email.delay(instance.pk)

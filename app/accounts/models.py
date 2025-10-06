from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', help_text='Владелец профиля.')
    avatar = models.ImageField(upload_to='profile_images', default='default.png', help_text='Аватар профиля.')
    bio = models.TextField(max_length=500, blank=True, help_text='Биография профиля.')

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.mail import send_mail
from django.conf import settings
from accounts.tokens import account_activation_token
from blog_celery import app
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User


@app.task
def send_email(pk):
    instance = User.objects.get(pk=pk)
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

from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.mail import send_mail
from django.conf import settings
from accounts.tokens import account_activation_token
from blog_celery import app
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from post.models import Post


@app.task
def post_share(slug, full_url, username, description, email_to):
    post = Post.objects.get(slug=slug)
    post_url = post.get_absolute_url()
    subject = f"{username} shared this post: {post.title}"
    message = f"{description} \n\n\n Check out this post at: {full_url}"
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [email_to],
    )

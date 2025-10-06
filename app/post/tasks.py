from django.core.mail import send_mail
from django.conf import settings
from blog_celery import app
from post.models import Post


@app.task
def post_share(slug, full_url, username, description, email_to):
    post = Post.objects.get(slug=slug)
    subject = f"{username} shared this post: {post.title}"
    message = f"{description}\n\n\n Check out this post at: {full_url}"
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [email_to],
    )

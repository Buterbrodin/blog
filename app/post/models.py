from django.db import models
from django.utils.text import slugify
from taggit.managers import TaggableManager
from django.contrib.auth.models import User
from django.urls import reverse


class Post(models.Model):
    title = models.CharField(max_length=100, verbose_name='Заголовок', help_text='Заголовок поста.')
    content = models.TextField(help_text='Содержание поста.')
    created_at = models.DateTimeField(auto_now_add=True, help_text='Дата создания поста.')
    updated_at = models.DateTimeField(auto_now=True, help_text='Дата обновления поста.')
    slug = models.SlugField(unique=True, help_text='Slug поста.')
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='posts',
                               help_text='Автора поста')
    views = models.IntegerField(default=0, help_text='Количество просмотров поста.')
    tags = TaggableManager(help_text='Теги поста.')

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['title']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('about', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Post.objects.filter(slug=slug).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Comment by {self.author} on {self.post}'

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at', 'post'])
        ]

from django.contrib import admin
from post.models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    fields = ['title', 'author', 'content', 'created_at', 'updated_at', 'slug', 'views', 'tags']
    readonly_fields = ['created_at', 'updated_at', 'slug']
    list_display = ['title', 'author', 'views', 'created_at', 'updated_at']
    list_filter = ['author__username', 'created_at', 'updated_at']
    search_fields = ['author__username', 'title', 'content']
    date_hierarchy = 'created_at'
    ordering = ['-created_at', 'author__username']

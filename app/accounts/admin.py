from django.contrib import admin
from accounts.models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'avatar', 'bio']
    list_filter = ['user']
    search_fields = ['user__username', 'bio']
    raw_id_fields = ['user']

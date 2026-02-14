from django.contrib import admin
from .models import Announcement, AnnouncementRead


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'priority', 'visibility', 'is_pinned', 'created_by', 'created_at')
    list_filter = ('category', 'priority', 'visibility', 'is_pinned', 'is_active')
    search_fields = ('title', 'content')


@admin.register(AnnouncementRead)
class AnnouncementReadAdmin(admin.ModelAdmin):
    list_display = ('announcement', 'user', 'read_at')
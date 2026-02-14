from django.contrib import admin
from .models import Notification, ActivityNotification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('student', 'requested_by', 'field_to_edit', 'status', 'created_at')
    list_filter = ('status', 'field_to_edit', 'created_at')
    search_fields = ('student__full_name', 'requested_by__full_name')


@admin.register(ActivityNotification)
class ActivityNotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'recipient__full_name')
from django.db import models
from django.conf import settings


class Notification(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    )

    FIELD_CHOICES = (
        ('full_name', 'Full Name'),
        ('phone', 'Phone Number'),
        ('email', 'Email Address'),
        ('parent_name', 'Parent Name'),
        ('parent_phone', 'Parent Phone'),
        ('address', 'Address'),
        ('roll_no', 'Roll Number'),
        ('prn', 'PRN Number'),
        ('other', 'Other'),
    )

    notification_type = models.CharField(max_length=30, default='edit_request')
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    student_file = models.ForeignKey(
        'students.StudentFile',
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_notifications'
    )
    field_to_edit = models.CharField(max_length=100, choices=FIELD_CHOICES)
    remark = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_read = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='resolved_notifications'
    )
    resolution_note = models.TextField(blank=True, default='')
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['requested_by']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.requested_by.full_name} → {self.student.full_name} ({self.status})"


class ActivityNotification(models.Model):
    """In-app notifications for various system events."""

    TYPE_CHOICES = (
        ('file_assigned', 'File Assigned'),
        ('file_uploaded', 'New File Uploaded'),
        ('announcement', 'New Announcement'),
        ('permission_granted', 'Permission Granted'),
        ('permission_revoked', 'Permission Revoked'),
        ('edit_resolved', 'Edit Request Resolved'),
        ('staff_created', 'Account Created'),
        ('password_changed', 'Password Changed'),
        ('general', 'General'),
    )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='activity_notifications'
    )
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='general')
    title = models.CharField(max_length=255)
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True, default='')
    is_read = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='created_activity_notifications'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'activity_notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.recipient.full_name}: {self.title}"

    @property
    def type_emoji(self):
        emojis = {
            'file_assigned': '📁',
            'file_uploaded': '📤',
            'announcement': '📢',
            'permission_granted': '✅',
            'permission_revoked': '❌',
            'edit_resolved': '✅',
            'staff_created': '👤',
            'password_changed': '🔑',
            'general': '📋',
        }
        return emojis.get(self.notification_type, '📋')

    @property
    def type_color(self):
        colors = {
            'file_assigned': '#4f46e5',
            'file_uploaded': '#06b6d4',
            'announcement': '#d97706',
            'permission_granted': '#16a34a',
            'permission_revoked': '#dc2626',
            'edit_resolved': '#16a34a',
            'staff_created': '#8b5cf6',
            'password_changed': '#f59e0b',
            'general': '#64748b',
        }
        return colors.get(self.notification_type, '#64748b')
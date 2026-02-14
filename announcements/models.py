from django.db import models
from django.conf import settings


class Announcement(models.Model):
    CATEGORY_CHOICES = (
        ('general', 'General'),
        ('exam', 'Exam'),
        ('holiday', 'Holiday'),
        ('event', 'Event'),
        ('urgent', 'Urgent'),
        ('academic', 'Academic'),
    )

    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
    )

    VISIBILITY_CHOICES = (
        ('all', 'Everyone'),
        ('hod', 'HODs Only'),
        ('teacher', 'Teachers Only'),
        ('guardian', 'Guardians Only'),
        ('staff', 'All Staff (HOD + Teacher + Guardian)'),
    )

    title = models.CharField(max_length=255)
    content = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='all')
    is_pinned = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    attachment = models.FileField(upload_to='announcements/', blank=True, null=True)
    attachment_name = models.CharField(max_length=255, blank=True, default='')

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='announcements'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'announcements'
        ordering = ['-is_pinned', '-created_at']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['visibility']),
            models.Index(fields=['is_pinned']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"

    @property
    def category_emoji(self):
        emojis = {
            'general': '📋',
            'exam': '📝',
            'holiday': '🎉',
            'event': '🎪',
            'urgent': '🚨',
            'academic': '🎓',
        }
        return emojis.get(self.category, '📋')

    @property
    def priority_color(self):
        colors = {
            'low': '#22c55e',
            'normal': '#3b82f6',
            'high': '#ef4444',
        }
        return colors.get(self.priority, '#3b82f6')

    @property
    def is_expired(self):
        if self.expires_at:
            from django.utils import timezone
            return timezone.now() > self.expires_at
        return False


class AnnouncementRead(models.Model):
    """Track which users have read which announcements."""
    announcement = models.ForeignKey(
        Announcement,
        on_delete=models.CASCADE,
        related_name='reads'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='read_announcements'
    )
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'announcement_reads'
        unique_together = ['announcement', 'user']

    def __str__(self):
        return f"{self.user.full_name} read {self.announcement.title}"
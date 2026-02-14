 
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('hod', 'HOD'),
        ('teacher', 'Teacher'),
        ('guardian', 'Teacher Guardian'),
    )

    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, blank=True, default='')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='teacher')
    department = models.CharField(max_length=100, blank=True, default='')
    photo = models.ImageField(upload_to='staff_photos/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        'self', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='created_users'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['department']),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_hod(self):
        return self.role == 'hod'

    @property
    def is_teacher(self):
        return self.role == 'teacher'

    @property
    def is_guardian(self):
        return self.role == 'guardian'

    @property
    def initials(self):
        if self.full_name:
            parts = self.full_name.strip().split()
            if len(parts) >= 2:
                return (parts[0][0] + parts[-1][0]).upper()
            elif len(parts) == 1:
                return parts[0][0].upper()
        return 'U'


class LoginAttempt(models.Model):
    username = models.CharField(max_length=150)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, default='')
    success = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'login_attempts'
        ordering = ['-timestamp']

    def __str__(self):
        status = 'Success' if self.success else 'Failed'
        return f"{self.username} - {status} - {self.timestamp}"


class AccountLockout(models.Model):
    username = models.CharField(max_length=150, unique=True)
    failed_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    last_failed = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'account_lockouts'

    def __str__(self):
        return f"{self.username} - {self.failed_attempts} attempts"


class SecurityLog(models.Model):
    ACTION_CHOICES = (
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('login_failed', 'Login Failed'),
        ('password_change', 'Password Change'),
        ('user_create', 'User Created'),
        ('user_edit', 'User Edited'),
        ('user_delete', 'User Deleted'),
        ('file_upload', 'File Upload'),
        ('file_delete', 'File Delete'),
        ('student_edit', 'Student Edit'),
        ('student_delete', 'Student Delete'),
        ('permission_change', 'Permission Change'),
        ('mark_edit', 'Mark Edit Request'),
        ('resolve_edit', 'Resolve Edit Request'),
        ('dismiss_notification', 'Dismiss Notification'),
        ('unauthorized_access', 'Unauthorized Access'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='security_logs'
    )
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, default='')
    details = models.TextField(blank=True, default='')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'security_logs'
        ordering = ['-timestamp']

    def __str__(self):
        user_str = self.user.username if self.user else 'Unknown'
        return f"{user_str} - {self.get_action_display()} - {self.timestamp}"
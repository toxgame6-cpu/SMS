from .models import ActivityNotification
from accounts.models import User


def send_activity_notification(recipient, notification_type, title, message, link='', created_by=None):
    """Send an activity notification to a specific user."""
    ActivityNotification.objects.create(
        recipient=recipient,
        notification_type=notification_type,
        title=title,
        message=message,
        link=link,
        created_by=created_by,
    )


def send_to_all_staff(notification_type, title, message, link='', created_by=None, exclude_user=None):
    """Send notification to all active staff (except admin and excluded user)."""
    staff = User.objects.filter(
        is_active=True,
        role__in=['hod', 'teacher', 'guardian']
    )
    if exclude_user:
        staff = staff.exclude(pk=exclude_user.pk)

    for user in staff:
        send_activity_notification(user, notification_type, title, message, link, created_by)


def send_to_admins(notification_type, title, message, link='', created_by=None):
    """Send notification to all admins."""
    admins = User.objects.filter(is_active=True, role='admin')
    for admin in admins:
        send_activity_notification(admin, notification_type, title, message, link, created_by)


def send_to_role(role, notification_type, title, message, link='', created_by=None):
    """Send notification to all users of a specific role."""
    users = User.objects.filter(is_active=True, role=role)
    for user in users:
        send_activity_notification(user, notification_type, title, message, link, created_by)
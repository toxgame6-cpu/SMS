def global_context(request):
    """Add global context variables to all templates."""
    context = {
        'user_role': None,
        'unread_notification_count': 0,
        'unread_announcement_count': 0,
        'unread_activity_count': 0,
    }

    if request.user.is_authenticated:
        context['user_role'] = request.user.role

        # Count unread notifications for admin
        if request.user.role == 'admin':
            from notifications.models import Notification
            context['unread_notification_count'] = Notification.objects.filter(
                is_read=False,
                status='pending'
            ).count()
        elif request.user.role in ('hod', 'teacher', 'guardian'):
            from notifications.models import Notification
            context['unread_notification_count'] = Notification.objects.filter(
                requested_by=request.user,
                status='pending'
            ).count()

        # Count unread announcements
        try:
            from announcements.models import AnnouncementRead
            from announcements.views import get_visible_announcements
            visible = get_visible_announcements(request.user)
            read_ids = AnnouncementRead.objects.filter(
                user=request.user
            ).values_list('announcement_id', flat=True)
            context['unread_announcement_count'] = visible.exclude(id__in=read_ids).count()
        except Exception:
            context['unread_announcement_count'] = 0

        # Count unread activity notifications
        try:
            from notifications.models import ActivityNotification
            context['unread_activity_count'] = ActivityNotification.objects.filter(
                recipient=request.user,
                is_read=False
            ).count()
        except Exception:
            context['unread_activity_count'] = 0

    return context
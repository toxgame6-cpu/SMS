from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone

from accounts.decorators import admin_required, role_required
from accounts.utils import log_action
from students.models import Student, StudentFile
from .models import Notification, ActivityNotification
from .forms import MarkEditForm


@login_required
@admin_required
def notification_list(request):
    """Admin notification center."""
    status_filter = request.GET.get('status', '')

    notifications = Notification.objects.select_related(
        'student', 'student_file', 'requested_by', 'resolved_by'
    ).all()

    if status_filter:
        notifications = notifications.filter(status=status_filter)

    paginator = Paginator(notifications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    counts = {
        'all': Notification.objects.count(),
        'pending': Notification.objects.filter(status='pending').count(),
        'resolved': Notification.objects.filter(status='resolved').count(),
        'dismissed': Notification.objects.filter(status='dismissed').count(),
    }

    return render(request, 'notifications/notification_list.html', {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'counts': counts,
    })


@login_required
@role_required('hod', 'teacher', 'guardian')
def my_requests(request):
    """Show user's own edit requests."""
    notifications = Notification.objects.filter(
        requested_by=request.user
    ).select_related('student', 'student_file', 'resolved_by')

    paginator = Paginator(notifications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'notifications/my_requests.html', {
        'page_obj': page_obj,
    })


@login_required
@role_required('hod', 'teacher', 'guardian')
def create_mark_edit(request):
    """Create a mark edit request."""
    if request.method == 'POST':
        form = MarkEditForm(request.POST)

        if form.is_valid():
            student_id = form.cleaned_data['student_id']
            field_to_edit = form.cleaned_data['field_to_edit']
            remark = form.cleaned_data['remark']

            student = get_object_or_404(Student, pk=student_id)

            if request.user.role in ('teacher', 'guardian'):
                from permissions_app.models import FilePermission
                if not FilePermission.objects.filter(
                    user=request.user, student_file=student.file
                ).exists():
                    messages.error(request, 'You do not have permission.')
                    return redirect('file_list')

            existing = Notification.objects.filter(
                student=student,
                requested_by=request.user,
                status='pending'
            ).exists()

            if existing:
                messages.warning(request, 'You already have a pending edit request for this student.')
                return redirect('student_list', file_id=student.file_id)

            Notification.objects.create(
                student=student,
                student_file=student.file,
                requested_by=request.user,
                field_to_edit=field_to_edit,
                remark=remark,
            )

            student.status = 'marked'
            student.save()

            # Send activity notification to admins
            from .utils import send_to_admins
            field_display = dict(Notification.FIELD_CHOICES).get(field_to_edit, field_to_edit)
            send_to_admins(
                'general',
                f'Edit Request: {student.full_name}',
                f'{request.user.full_name} ({request.user.get_role_display()}) wants to edit {field_display} for {student.full_name}. Remark: {remark}',
                f'/notifications/',
                created_by=request.user
            )

            log_action(request.user, 'mark_edit', request,
                       f'Marked edit for {student.full_name}: {field_to_edit}')
            messages.success(request, 'Edit request submitted to Admin!')

            return redirect('student_list', file_id=student.file_id)

    messages.error(request, 'Invalid request.')
    return redirect('file_list')


@login_required
@admin_required
def resolve_notification(request, pk):
    """Resolve a notification."""
    notification = get_object_or_404(Notification, pk=pk)

    if request.method == 'POST':
        notification.status = 'resolved'
        notification.is_read = True
        notification.resolved_by = request.user
        notification.resolved_at = timezone.now()
        notification.resolution_note = request.POST.get('resolution_note', '')
        notification.save()

        student = notification.student
        other_pending = Notification.objects.filter(
            student=student, status='pending'
        ).exclude(pk=pk).exists()

        if not other_pending:
            student.status = 'normal'
            student.save()

        # Notify the requester that their edit request was resolved
        from .utils import send_activity_notification
        send_activity_notification(
            notification.requested_by,
            'edit_resolved',
            f'Edit Request Resolved: {student.full_name}',
            f'Your edit request for {student.full_name} has been resolved by {request.user.full_name}.',
            f'/students/{student.pk}/',
            created_by=request.user
        )

        log_action(request.user, 'resolve_edit', request,
                   f'Resolved edit request for {student.full_name}')
        messages.success(request, 'Notification resolved!')

    return redirect('notification_list')


@login_required
@admin_required
def dismiss_notification(request, pk):
    """Dismiss a notification."""
    notification = get_object_or_404(Notification, pk=pk)

    if request.method == 'POST':
        notification.status = 'dismissed'
        notification.is_read = True
        notification.save()

        student = notification.student
        other_pending = Notification.objects.filter(
            student=student, status='pending'
        ).exclude(pk=pk).exists()

        if not other_pending:
            student.status = 'normal'
            student.save()

        log_action(request.user, 'dismiss_notification', request,
                   f'Dismissed notification for {student.full_name}')
        messages.info(request, 'Notification dismissed.')

    return redirect('notification_list')


@login_required
@admin_required
def mark_all_read(request):
    """Mark all notifications as read."""
    if request.method == 'POST':
        Notification.objects.filter(is_read=False).update(is_read=True)
        messages.success(request, 'All notifications marked as read.')

    return redirect('notification_list')


# ===== ACTIVITY FEED VIEWS =====

@login_required
def activity_feed(request):
    """Show activity feed for current user."""
    type_filter = request.GET.get('type', '')

    activities = ActivityNotification.objects.filter(
        recipient=request.user
    ).select_related('created_by')

    if type_filter:
        activities = activities.filter(notification_type=type_filter)

    unread_count = activities.filter(is_read=False).count()

    paginator = Paginator(activities, 15)
    page_obj = paginator.get_page(request.GET.get('page'))

    type_choices = ActivityNotification.TYPE_CHOICES

    return render(request, 'notifications/activity_feed.html', {
        'page_obj': page_obj,
        'type_filter': type_filter,
        'unread_count': unread_count,
        'type_choices': type_choices,
    })


@login_required
def mark_activity_read(request, pk):
    """Mark single activity as read."""
    activity = get_object_or_404(ActivityNotification, pk=pk, recipient=request.user)
    activity.is_read = True
    activity.save()

    if activity.link:
        return redirect(activity.link)
    return redirect('activity_feed')


@login_required
def mark_all_activities_read(request):
    """Mark all activities as read."""
    if request.method == 'POST':
        ActivityNotification.objects.filter(
            recipient=request.user, is_read=False
        ).update(is_read=True)
        messages.success(request, 'All notifications marked as read!')

    return redirect('activity_feed')
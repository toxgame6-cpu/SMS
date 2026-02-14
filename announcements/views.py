from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone

from accounts.decorators import role_required, admin_required
from accounts.utils import log_action
from .models import Announcement, AnnouncementRead
from .forms import AnnouncementForm


def get_visible_announcements(user):
    """Get announcements visible to a specific user based on their role."""
    announcements = Announcement.objects.filter(is_active=True)

    # Filter out expired announcements
    announcements = announcements.filter(
        Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
    )

    # Filter by visibility
    if user.role == 'admin':
        # Admin sees all
        pass
    elif user.role == 'hod':
        announcements = announcements.filter(
            Q(visibility='all') | Q(visibility='hod') | Q(visibility='staff')
        )
    elif user.role == 'teacher':
        announcements = announcements.filter(
            Q(visibility='all') | Q(visibility='teacher') | Q(visibility='staff')
        )
    elif user.role == 'guardian':
        announcements = announcements.filter(
            Q(visibility='all') | Q(visibility='guardian') | Q(visibility='staff')
        )

    return announcements


@login_required
def announcement_list(request):
    """List all announcements for the current user."""
    category_filter = request.GET.get('category', '')
    search = request.GET.get('search', '')

    announcements = get_visible_announcements(request.user)

    if category_filter:
        announcements = announcements.filter(category=category_filter)

    if search:
        announcements = announcements.filter(
            Q(title__icontains=search) | Q(content__icontains=search)
        )

    # Get read status for current user
    read_ids = set(
        AnnouncementRead.objects.filter(
            user=request.user
        ).values_list('announcement_id', flat=True)
    )

    # Count unread
    unread_count = announcements.exclude(id__in=read_ids).count()

    paginator = Paginator(announcements, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'announcements/announcement_list.html', {
        'page_obj': page_obj,
        'category_filter': category_filter,
        'search': search,
        'read_ids': read_ids,
        'unread_count': unread_count,
        'categories': Announcement.CATEGORY_CHOICES,
    })


@login_required
def announcement_detail(request, pk):
    """View single announcement detail."""
    announcement = get_object_or_404(Announcement, pk=pk, is_active=True)

    # Check visibility
    user = request.user
    if user.role != 'admin':
        visible = get_visible_announcements(user).filter(pk=pk).exists()
        if not visible:
            messages.error(request, 'You do not have permission to view this announcement.')
            return redirect('announcement_list')

    # Mark as read
    AnnouncementRead.objects.get_or_create(
        announcement=announcement,
        user=request.user
    )

    return render(request, 'announcements/announcement_detail.html', {
        'announcement': announcement,
    })


@login_required
@role_required('admin', 'hod')
def announcement_create(request):
    """Create a new announcement. Admin and HOD can create."""
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.created_by = request.user

            # Save attachment name
            if announcement.attachment:
                announcement.attachment_name = announcement.attachment.name

            announcement.save()

                        # Send activity notifications to relevant users
            from notifications.utils import send_activity_notification, send_to_all_staff, send_to_role
            from accounts.models import User

            if announcement.visibility == 'all':
                send_to_all_staff(
                    'announcement',
                    f'New Announcement: {announcement.title}',
                    f'{announcement.get_category_display()} announcement by {request.user.full_name}: {announcement.content[:100]}...',
                    f'/announcements/{announcement.pk}/',
                    created_by=request.user
                )
            elif announcement.visibility == 'staff':
                send_to_all_staff(
                    'announcement',
                    f'New Announcement: {announcement.title}',
                    f'{announcement.get_category_display()} announcement by {request.user.full_name}: {announcement.content[:100]}...',
                    f'/announcements/{announcement.pk}/',
                    created_by=request.user
                )
            elif announcement.visibility in ('hod', 'teacher', 'guardian'):
                send_to_role(
                    announcement.visibility,
                    'announcement',
                    f'New Announcement: {announcement.title}',
                    f'{announcement.get_category_display()} announcement by {request.user.full_name}: {announcement.content[:100]}...',
                    f'/announcements/{announcement.pk}/',
                    created_by=request.user
                )

            log_action(request.user, 'user_create', request,
                       f'Created announcement: {announcement.title}')
            messages.success(request, f'Announcement "{announcement.title}" published successfully!')
            return redirect('announcement_list')
    else:
        form = AnnouncementForm()

    # If HOD, limit visibility options
    if request.user.role == 'hod':
        form.fields['visibility'].choices = [
            ('all', 'Everyone'),
            ('teacher', 'Teachers Only'),
            ('guardian', 'Guardians Only'),
            ('staff', 'All Staff'),
        ]

    return render(request, 'announcements/announcement_create.html', {
        'form': form,
    })


@login_required
@role_required('admin', 'hod')
def announcement_edit(request, pk):
    """Edit an announcement."""
    announcement = get_object_or_404(Announcement, pk=pk, is_active=True)

    # HOD can only edit their own announcements
    if request.user.role == 'hod' and announcement.created_by != request.user:
        messages.error(request, 'You can only edit your own announcements.')
        return redirect('announcement_list')

    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES, instance=announcement)
        if form.is_valid():
            updated = form.save(commit=False)
            if updated.attachment:
                updated.attachment_name = updated.attachment.name
            updated.save()

            log_action(request.user, 'user_edit', request,
                       f'Edited announcement: {updated.title}')
            messages.success(request, f'Announcement "{updated.title}" updated!')
            return redirect('announcement_detail', pk=announcement.pk)
    else:
        form = AnnouncementForm(instance=announcement)

    if request.user.role == 'hod':
        form.fields['visibility'].choices = [
            ('all', 'Everyone'),
            ('teacher', 'Teachers Only'),
            ('guardian', 'Guardians Only'),
            ('staff', 'All Staff'),
        ]

    return render(request, 'announcements/announcement_edit.html', {
        'form': form,
        'announcement': announcement,
    })


@login_required
@role_required('admin', 'hod')
def announcement_delete(request, pk):
    """Delete an announcement."""
    announcement = get_object_or_404(Announcement, pk=pk, is_active=True)

    # HOD can only delete their own
    if request.user.role == 'hod' and announcement.created_by != request.user:
        messages.error(request, 'You can only delete your own announcements.')
        return redirect('announcement_list')

    if request.method == 'POST':
        title = announcement.title
        announcement.is_active = False
        announcement.save()

        log_action(request.user, 'user_delete', request,
                   f'Deleted announcement: {title}')
        messages.success(request, f'Announcement "{title}" deleted!')

    return redirect('announcement_list')


@login_required
@role_required('admin', 'hod')
def announcement_toggle_pin(request, pk):
    """Toggle pin status of announcement."""
    announcement = get_object_or_404(Announcement, pk=pk, is_active=True)

    if request.method == 'POST':
        announcement.is_pinned = not announcement.is_pinned
        announcement.save()

        status = 'pinned' if announcement.is_pinned else 'unpinned'
        messages.success(request, f'Announcement "{announcement.title}" {status}!')

    return redirect('announcement_list')


@login_required
def mark_all_announcements_read(request):
    """Mark all visible announcements as read."""
    if request.method == 'POST':
        visible = get_visible_announcements(request.user)

        for announcement in visible:
            AnnouncementRead.objects.get_or_create(
                announcement=announcement,
                user=request.user
            )

        messages.success(request, 'All announcements marked as read!')

    return redirect('announcement_list')
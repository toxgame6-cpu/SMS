from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from accounts.decorators import admin_required
from accounts.models import User
from accounts.utils import log_action
from students.models import StudentFile
from .models import FilePermission


@login_required
@admin_required
def permission_list(request):
    """Show permission management page."""
    search = request.GET.get('search', '')

    staff = User.objects.filter(
        role__in=['teacher', 'guardian'],
        is_active=True
    ).order_by('role', 'full_name')

    if search:
        from django.db.models import Q
        staff = staff.filter(
            Q(full_name__icontains=search) |
            Q(email__icontains=search)
        )

    files = StudentFile.objects.filter(is_active=True).order_by('file_name')

    permissions = {}
    for s in staff:
        permissions[s.id] = set(
            FilePermission.objects.filter(user=s).values_list('student_file_id', flat=True)
        )

    return render(request, 'permissions/manage_permissions.html', {
        'staff': staff,
        'files': files,
        'permissions': permissions,
        'search': search,
    })


@login_required
@admin_required
def permission_save(request, user_id):
    """Save permissions for a user."""
    if request.method == 'POST':
        user = get_object_or_404(User, pk=user_id, is_active=True)

        # Get old permissions for comparison
        old_file_ids = set(
            FilePermission.objects.filter(user=user).values_list('student_file_id', flat=True)
        )

        selected_files = request.POST.getlist('files')
        selected_file_ids = set(int(f) for f in selected_files if f.isdigit())

        # Find newly granted and revoked
        newly_granted = selected_file_ids - old_file_ids
        revoked = old_file_ids - selected_file_ids

        # Delete all existing and create new
        FilePermission.objects.filter(user=user).delete()

        for file_id in selected_files:
            try:
                student_file = StudentFile.objects.get(pk=file_id, is_active=True)
                FilePermission.objects.create(
                    user=user,
                    student_file=student_file,
                    granted_by=request.user,
                )
            except StudentFile.DoesNotExist:
                continue

        # Send activity notifications
        from notifications.utils import send_activity_notification

        for file_id in newly_granted:
            try:
                sf = StudentFile.objects.get(pk=file_id)
                send_activity_notification(
                    user,
                    'file_assigned',
                    f'New File Assigned: {sf.file_name}',
                    f'You have been granted access to "{sf.file_name}" ({sf.class_name} Div {sf.division} {sf.year}). You can now view its students.',
                    f'/files/{sf.pk}/',
                    created_by=request.user
                )
            except StudentFile.DoesNotExist:
                pass

        for file_id in revoked:
            try:
                sf = StudentFile.objects.get(pk=file_id)
                send_activity_notification(
                    user,
                    'permission_revoked',
                    f'File Access Removed: {sf.file_name}',
                    f'Your access to "{sf.file_name}" has been revoked by admin.',
                    '',
                    created_by=request.user
                )
            except StudentFile.DoesNotExist:
                pass

        log_action(request.user, 'permission_change', request,
                   f'Updated permissions for {user.full_name}: {len(selected_files)} files')
        messages.success(request, f'Permissions updated for {user.full_name}!')

    return redirect('permission_list')
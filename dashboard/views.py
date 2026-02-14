 
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required


@login_required
def dashboard_redirect(request):
    """Redirect to appropriate dashboard based on role."""
    role_dashboards = {
        'admin': '/admin-panel/',
        'hod': '/hod-panel/',
        'teacher': '/teacher-panel/',
        'guardian': '/guardian-panel/',
    }
    return redirect(role_dashboards.get(request.user.role, '/'))


@login_required
@role_required('admin')
def admin_dashboard(request):
    """Admin dashboard with stats."""
    from accounts.models import User, SecurityLog
    from students.models import StudentFile, Student
    from notifications.models import Notification
    from announcements.models import Announcement

    stats = {
        'total_teachers': User.objects.filter(role='teacher', is_active=True).count(),
        'total_guardians': User.objects.filter(role='guardian', is_active=True).count(),
        'total_hods': User.objects.filter(role='hod', is_active=True).count(),
        'total_students': Student.objects.count(),
        'total_files': StudentFile.objects.filter(is_active=True).count(),
        'pending_notifications': Notification.objects.filter(status='pending').count(),
    }

    recent_activity = SecurityLog.objects.select_related('user').all()[:10]
    recent_announcements = Announcement.objects.filter(is_active=True)[:5]

    return render(request, 'dashboard/admin_dashboard.html', {
        'stats': stats,
        'recent_activity': recent_activity,
        'recent_announcements': recent_announcements,
    })


@login_required
@role_required('hod')
def hod_dashboard(request):
    """HOD dashboard - sees all files."""
    from students.models import StudentFile, Student
    from notifications.models import Notification

    stats = {
        'total_files': StudentFile.objects.filter(is_active=True).count(),
        'total_students': Student.objects.count(),
        'my_requests': Notification.objects.filter(requested_by=request.user).count(),
        'pending_requests': Notification.objects.filter(
            requested_by=request.user, status='pending'
        ).count(),
    }

    return render(request, 'dashboard/hod_dashboard.html', {
        'stats': stats,
    })


@login_required
@role_required('teacher')
def teacher_dashboard(request):
    """Teacher dashboard - sees only assigned files."""
    from permissions_app.models import FilePermission
    from students.models import Student
    from notifications.models import Notification

    assigned_files = FilePermission.objects.filter(
        user=request.user
    ).select_related('student_file')

    file_ids = assigned_files.values_list('student_file_id', flat=True)
    total_students = Student.objects.filter(file_id__in=file_ids).count()

    stats = {
        'assigned_files': assigned_files.count(),
        'total_students': total_students,
        'my_requests': Notification.objects.filter(requested_by=request.user).count(),
        'pending_requests': Notification.objects.filter(
            requested_by=request.user, status='pending'
        ).count(),
    }

    return render(request, 'dashboard/teacher_dashboard.html', {
        'stats': stats,
    })


@login_required
@role_required('guardian')
def guardian_dashboard(request):
    """Guardian dashboard - same as teacher."""
    from permissions_app.models import FilePermission
    from students.models import Student
    from notifications.models import Notification

    assigned_files = FilePermission.objects.filter(
        user=request.user
    ).select_related('student_file')

    file_ids = assigned_files.values_list('student_file_id', flat=True)
    total_students = Student.objects.filter(file_id__in=file_ids).count()

    stats = {
        'assigned_files': assigned_files.count(),
        'total_students': total_students,
        'my_requests': Notification.objects.filter(requested_by=request.user).count(),
        'pending_requests': Notification.objects.filter(
            requested_by=request.user, status='pending'
        ).count(),
    }

    return render(request, 'dashboard/guardian_dashboard.html', {
        'stats': stats,
    })
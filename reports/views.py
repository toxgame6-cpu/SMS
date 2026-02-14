import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from accounts.decorators import admin_required, role_required
from accounts.models import User, SecurityLog
from students.models import StudentFile, Student
from notifications.models import Notification
from announcements.models import Announcement


@login_required
@admin_required
def reports_dashboard(request):
    """Main reports page with charts and analytics."""

    # === STUDENT STATISTICS ===

    # Class-wise student count
    class_wise = Student.objects.values('class_name').annotate(
        count=Count('id')
    ).order_by('class_name')
    class_labels = [item['class_name'] for item in class_wise]
    class_data = [item['count'] for item in class_wise]

    # Division-wise distribution
    division_wise = Student.objects.values('division').annotate(
        count=Count('id')
    ).order_by('division')
    division_labels = [f"Division {item['division']}" for item in division_wise]
    division_data = [item['count'] for item in division_wise]

    # Year-wise distribution
    year_wise = Student.objects.values('year').annotate(
        count=Count('id')
    ).order_by('year')
    year_labels = [item['year'] for item in year_wise]
    year_data = [item['count'] for item in year_wise]

    # Status-wise distribution
    status_wise = Student.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    status_labels = [item['status'].title() for item in status_wise]
    status_data = [item['count'] for item in status_wise]

    # === STAFF STATISTICS ===

    # Department-wise staff count
    dept_wise = User.objects.filter(
        is_active=True
    ).exclude(department='').values('department').annotate(
        count=Count('id')
    ).order_by('department')
    dept_labels = [item['department'] for item in dept_wise]
    dept_data = [item['count'] for item in dept_wise]

    # Role-wise staff count
    role_wise = User.objects.filter(
        is_active=True
    ).values('role').annotate(
        count=Count('id')
    ).order_by('role')
    role_map = {'admin': 'Admin', 'hod': 'HOD', 'teacher': 'Teacher', 'guardian': 'Guardian'}
    role_labels = [role_map.get(item['role'], item['role']) for item in role_wise]
    role_data = [item['count'] for item in role_wise]

    # === UPLOAD HISTORY ===

    # Last 30 days upload history
    thirty_days_ago = timezone.now() - timedelta(days=30)
    upload_history = StudentFile.objects.filter(
        upload_date__gte=thirty_days_ago,
        is_active=True
    ).values('upload_date__date').annotate(
        count=Count('id'),
        students=Count('students')
    ).order_by('upload_date__date')

    upload_dates = [item['upload_date__date'].strftime('%d %b') for item in upload_history]
    upload_counts = [item['count'] for item in upload_history]
    upload_student_counts = [item['students'] for item in upload_history]

    # === NOTIFICATION STATISTICS ===

    notif_stats = {
        'total': Notification.objects.count(),
        'pending': Notification.objects.filter(status='pending').count(),
        'resolved': Notification.objects.filter(status='resolved').count(),
        'dismissed': Notification.objects.filter(status='dismissed').count(),
    }

    # Most requested edit fields
    field_wise = Notification.objects.values('field_to_edit').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    field_map = dict(Notification.FIELD_CHOICES)
    field_labels = [field_map.get(item['field_to_edit'], item['field_to_edit']) for item in field_wise]
    field_data = [item['count'] for item in field_wise]

    # === SUMMARY NUMBERS ===

    summary = {
        'total_students': Student.objects.count(),
        'total_files': StudentFile.objects.filter(is_active=True).count(),
        'total_teachers': User.objects.filter(role='teacher', is_active=True).count(),
        'total_guardians': User.objects.filter(role='guardian', is_active=True).count(),
        'total_hods': User.objects.filter(role='hod', is_active=True).count(),
        'total_staff': User.objects.filter(is_active=True).count(),
        'total_announcements': Announcement.objects.filter(is_active=True).count(),
        'total_notifications': Notification.objects.count(),
        'logins_today': SecurityLog.objects.filter(
            action='login',
            timestamp__date=timezone.now().date()
        ).count(),
        'actions_today': SecurityLog.objects.filter(
            timestamp__date=timezone.now().date()
        ).count(),
    }

    # === RECENT UPLOADS ===

    recent_uploads = StudentFile.objects.filter(
        is_active=True
    ).select_related('uploaded_by').order_by('-upload_date')[:10]

    # === TOP ACTIVE USERS ===

    active_users = SecurityLog.objects.filter(
        timestamp__gte=thirty_days_ago
    ).values('user__full_name', 'user__role').annotate(
        action_count=Count('id')
    ).order_by('-action_count')[:5]

    context = {
        'summary': summary,
        'notif_stats': notif_stats,
        'recent_uploads': recent_uploads,
        'active_users': active_users,
        # Chart data as JSON
        'class_labels': json.dumps(class_labels),
        'class_data': json.dumps(class_data),
        'division_labels': json.dumps(division_labels),
        'division_data': json.dumps(division_data),
        'year_labels': json.dumps(year_labels),
        'year_data': json.dumps(year_data),
        'status_labels': json.dumps(status_labels),
        'status_data': json.dumps(status_data),
        'dept_labels': json.dumps(dept_labels),
        'dept_data': json.dumps(dept_data),
        'role_labels': json.dumps(role_labels),
        'role_data': json.dumps(role_data),
        'upload_dates': json.dumps(upload_dates),
        'upload_counts': json.dumps(upload_counts),
        'field_labels': json.dumps(field_labels),
        'field_data': json.dumps(field_data),
    }

    return render(request, 'reports/reports_dashboard.html', context)


@login_required
@admin_required
def export_summary_pdf(request):
    """Export summary report as PDF."""
    from io import BytesIO
    from django.template.loader import render_to_string

    summary = {
        'total_students': Student.objects.count(),
        'total_files': StudentFile.objects.filter(is_active=True).count(),
        'total_teachers': User.objects.filter(role='teacher', is_active=True).count(),
        'total_guardians': User.objects.filter(role='guardian', is_active=True).count(),
        'total_hods': User.objects.filter(role='hod', is_active=True).count(),
        'total_announcements': Announcement.objects.filter(is_active=True).count(),
        'pending_notifications': Notification.objects.filter(status='pending').count(),
    }

    class_wise = Student.objects.values('class_name').annotate(
        count=Count('id')
    ).order_by('class_name')

    division_wise = Student.objects.values('division').annotate(
        count=Count('id')
    ).order_by('division')

    year_wise = Student.objects.values('year').annotate(
        count=Count('id')
    ).order_by('year')

    recent_files = StudentFile.objects.filter(
        is_active=True
    ).order_by('-upload_date')[:10]

    staff_by_dept = User.objects.filter(
        is_active=True
    ).exclude(department='').values('department', 'role').annotate(
        count=Count('id')
    ).order_by('department', 'role')

    try:
        from xhtml2pdf import pisa

        html_string = render_to_string('reports/summary_pdf.html', {
            'summary': summary,
            'class_wise': class_wise,
            'division_wise': division_wise,
            'year_wise': year_wise,
            'recent_files': recent_files,
            'staff_by_dept': staff_by_dept,
            'generated_at': timezone.now(),
        })

        result = BytesIO()
        pdf = pisa.CreatePDF(BytesIO(html_string.encode('utf-8')), dest=result)

        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="SMS_Summary_Report_{timezone.now().strftime("%Y%m%d")}.pdf"'
            return response

    except ImportError:
        pass

    from django.contrib import messages
    messages.error(request, 'PDF generation not available.')
    return render(request, 'reports/reports_dashboard.html')
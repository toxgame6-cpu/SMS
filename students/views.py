 
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse, Http404
from django.conf import settings
from django.db.models import Q

from accounts.decorators import admin_required, role_required
from accounts.utils import log_action
from .models import StudentFile, Student
from .forms import ExcelUploadForm, StudentEditForm
from .utils import parse_excel, export_students_excel


@login_required
@admin_required
def upload_excel(request):
    """Upload Excel file with student data."""
    form = ExcelUploadForm()

    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)

        if form.is_valid():
            class_name = form.cleaned_data['class_name']
            division = form.cleaned_data['division']
            year = form.cleaned_data['year']
            academic_year = form.cleaned_data['academic_year']
            excel_file = form.cleaned_data['excel_file']

            # Validate file extension
            ext = os.path.splitext(excel_file.name)[1].lower()
            if ext not in settings.ALLOWED_EXCEL_EXTENSIONS:
                messages.error(request, 'Only .xlsx and .xls files are allowed.')
                return render(request, 'students/upload_excel.html', {'form': form})

            # Validate file size
            if excel_file.size > settings.MAX_UPLOAD_SIZE:
                messages.error(request, 'File size exceeds 10MB limit.')
                return render(request, 'students/upload_excel.html', {'form': form})

            # Check for duplicate
            if StudentFile.objects.filter(
                class_name=class_name,
                division=division,
                year=year,
                academic_year=academic_year,
                is_active=True
            ).exists():
                messages.error(request, 'A file for this class/division/year/academic year already exists.')
                return render(request, 'students/upload_excel.html', {'form': form})

            # Parse Excel
            students_data, errors = parse_excel(excel_file)

            if not students_data and errors:
                for error in errors:
                    messages.error(request, error)
                return render(request, 'students/upload_excel.html', {'form': form})

            # Generate file name
            file_name = f"{year}_{division}_{class_name}_{academic_year}"

            # Create StudentFile
            student_file = StudentFile.objects.create(
                file_name=file_name,
                class_name=class_name,
                division=division,
                year=year,
                academic_year=academic_year,
                excel_file=excel_file,
                uploaded_by=request.user,
                total_students=len(students_data),
            )

            # Create Students
            student_objects = []
            for data in students_data:
                student_objects.append(Student(
                    file=student_file,
                    roll_no=data['roll_no'],
                    prn=data['prn'],
                    full_name=data['full_name'],
                    phone=data['phone'],
                    email=data['email'],
                    parent_name=data['parent_name'],
                    parent_phone=data['parent_phone'],
                    address=data['address'],
                    class_name=class_name,
                    division=division,
                    year=year,
                ))

            Student.objects.bulk_create(student_objects)

            log_action(request.user, 'file_upload', request,
                       f'Uploaded {file_name} with {len(students_data)} students')

            success_msg = f'File uploaded successfully! {len(students_data)} students imported.'
            if errors:
                success_msg += f' ({len(errors)} rows skipped)'
            messages.success(request, success_msg)

            if errors:
                for error in errors[:5]:  # Show max 5 errors
                    messages.warning(request, error)

            return redirect('file_list')

    return render(request, 'students/upload_excel.html', {'form': form})


@login_required
def file_list(request):
    """List all student files."""
    user = request.user
    search = request.GET.get('search', '')
    year_filter = request.GET.get('year', '')

    if user.role == 'admin' or user.role == 'hod':
        files = StudentFile.objects.filter(is_active=True)
    elif user.role in ('teacher', 'guardian'):
        from permissions_app.models import FilePermission
        allowed_file_ids = FilePermission.objects.filter(
            user=user
        ).values_list('student_file_id', flat=True)
        files = StudentFile.objects.filter(id__in=allowed_file_ids, is_active=True)
    else:
        files = StudentFile.objects.none()

    if search:
        files = files.filter(
            Q(file_name__icontains=search) |
            Q(class_name__icontains=search) |
            Q(division__icontains=search)
        )

    if year_filter:
        files = files.filter(year=year_filter)

    years = StudentFile.objects.filter(is_active=True).values_list(
        'year', flat=True
    ).distinct().order_by('year')

    paginator = Paginator(files, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'students/file_list.html', {
        'page_obj': page_obj,
        'search': search,
        'years': years,
        'selected_year': year_filter,
    })


@login_required
def student_list(request, file_id):
    """List students in a file."""
    student_file = get_object_or_404(StudentFile, pk=file_id, is_active=True)

    # Permission check
    user = request.user
    if user.role in ('teacher', 'guardian'):
        from permissions_app.models import FilePermission
        if not FilePermission.objects.filter(user=user, student_file=student_file).exists():
            messages.error(request, 'You do not have permission to view this file.')
            return redirect('file_list')

    search = request.GET.get('search', '')
    students = student_file.students.all()

    if search:
        students = students.filter(
            Q(full_name__icontains=search) |
            Q(roll_no__icontains=search) |
            Q(prn__icontains=search)
        )

    paginator = Paginator(students, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'students/student_list.html', {
        'student_file': student_file,
        'page_obj': page_obj,
        'search': search,
    })


@login_required
def student_profile(request, pk):
    """View full student profile."""
    student = get_object_or_404(Student, pk=pk)

    # Permission check
    user = request.user
    if user.role in ('teacher', 'guardian'):
        from permissions_app.models import FilePermission
        if not FilePermission.objects.filter(user=user, student_file=student.file).exists():
            messages.error(request, 'You do not have permission to view this student.')
            return redirect('file_list')

    return render(request, 'students/student_profile.html', {
        'student': student,
    })


@login_required
@admin_required
def student_edit(request, pk):
    """Edit student record."""
    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST':
        form = StudentEditForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            log_action(request.user, 'student_edit', request,
                       f'Edited student: {student.full_name}')
            messages.success(request, f'Student "{student.full_name}" updated successfully!')
            return redirect('student_profile', pk=student.pk)
    else:
        form = StudentEditForm(instance=student)

    return render(request, 'students/student_edit.html', {
        'form': form,
        'student': student,
    })


@login_required
@admin_required
def student_delete(request, pk):
    """Delete a student."""
    student = get_object_or_404(Student, pk=pk)
    file_id = student.file_id

    if request.method == 'POST':
        student_name = student.full_name
        student.delete()

        # Update file count
        student_file = StudentFile.objects.get(pk=file_id)
        student_file.total_students = student_file.students.count()
        student_file.save()

        log_action(request.user, 'student_delete', request,
                   f'Deleted student: {student_name}')
        messages.success(request, f'Student "{student_name}" deleted successfully!')

    return redirect('student_list', file_id=file_id)


@login_required
@admin_required
def file_delete(request, file_id):
    """Delete a student file and all its students."""
    student_file = get_object_or_404(StudentFile, pk=file_id, is_active=True)

    if request.method == 'POST':
        file_name = student_file.file_name
        student_file.is_active = False
        student_file.save()

        log_action(request.user, 'file_delete', request,
                   f'Deleted file: {file_name}')
        messages.success(request, f'File "{file_name}" deleted successfully!')

    return redirect('file_list')


@login_required
def file_download(request, file_id):
    """Download students as Excel."""
    student_file = get_object_or_404(StudentFile, pk=file_id, is_active=True)

    # Permission check
    user = request.user
    if user.role in ('teacher', 'guardian'):
        from permissions_app.models import FilePermission
        if not FilePermission.objects.filter(user=user, student_file=student_file).exists():
            messages.error(request, 'You do not have permission to download this file.')
            return redirect('file_list')

    students = student_file.students.all()
    return export_students_excel(students, student_file.file_name)


@login_required
def my_assigned_files(request):
    """Show files assigned to teacher/guardian."""
    from permissions_app.models import FilePermission

    assigned = FilePermission.objects.filter(
        user=request.user
    ).select_related('student_file')

    file_ids = assigned.values_list('student_file_id', flat=True)
    files = StudentFile.objects.filter(id__in=file_ids, is_active=True)

    paginator = Paginator(files, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'students/file_list.html', {
        'page_obj': page_obj,
        'search': '',
        'years': [],
        'selected_year': '',
    })

@login_required
def student_pdf(request, pk):
    """Generate PDF for student profile."""
    student = get_object_or_404(Student, pk=pk)

    # Permission check
    user = request.user
    if user.role in ('teacher', 'guardian'):
        from permissions_app.models import FilePermission
        if not FilePermission.objects.filter(user=user, student_file=student.file).exists():
            messages.error(request, 'You do not have permission to download this student profile.')
            return redirect('file_list')

    try:
        from xhtml2pdf import pisa
        from io import BytesIO
        from django.template.loader import render_to_string

        html_string = render_to_string('students/student_pdf.html', {
            'student': student,
        })

        result = BytesIO()
        pdf = pisa.CreatePDF(BytesIO(html_string.encode('utf-8')), dest=result)

        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{student.full_name}_Profile.pdf"'
            return response
        else:
            messages.error(request, 'Error generating PDF.')
            return redirect('student_profile', pk=pk)

    except ImportError:
        messages.error(request, 'PDF generation is not available. Please install xhtml2pdf.')
        return redirect('student_profile', pk=pk)
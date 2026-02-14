from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from accounts.decorators import admin_required
from accounts.models import User
from accounts.utils import log_action
from .forms import StaffCreateForm, StaffEditForm


@login_required
@admin_required
def teacher_list(request):
    search = request.GET.get('search', '')
    department = request.GET.get('department', '')

    teachers = User.objects.filter(role='teacher', is_active=True).order_by('-created_at')

    if search:
        teachers = teachers.filter(
            Q(full_name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )

    if department:
        teachers = teachers.filter(department=department)

    departments = User.objects.filter(
        role='teacher', is_active=True
    ).exclude(department='').values_list('department', flat=True).distinct().order_by('department')

    paginator = Paginator(teachers, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'staff/teacher_list.html', {
        'page_obj': page_obj,
        'search': search,
        'departments': departments,
        'selected_department': department,
        'staff_type': 'teacher',
    })


@login_required
@admin_required
def guardian_list(request):
    search = request.GET.get('search', '')
    department = request.GET.get('department', '')

    guardians = User.objects.filter(role='guardian', is_active=True).order_by('-created_at')

    if search:
        guardians = guardians.filter(
            Q(full_name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )

    if department:
        guardians = guardians.filter(department=department)

    departments = User.objects.filter(
        role='guardian', is_active=True
    ).exclude(department='').values_list('department', flat=True).distinct().order_by('department')

    paginator = Paginator(guardians, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'staff/guardian_list.html', {
        'page_obj': page_obj,
        'search': search,
        'departments': departments,
        'selected_department': department,
        'staff_type': 'guardian',
    })


@login_required
@admin_required
def hod_list(request):
    search = request.GET.get('search', '')
    department = request.GET.get('department', '')

    hods = User.objects.filter(role='hod', is_active=True).order_by('-created_at')

    if search:
        hods = hods.filter(
            Q(full_name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )

    if department:
        hods = hods.filter(department=department)

    departments = User.objects.filter(
        role='hod', is_active=True
    ).exclude(department='').values_list('department', flat=True).distinct().order_by('department')

    paginator = Paginator(hods, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'staff/hod_list.html', {
        'page_obj': page_obj,
        'search': search,
        'departments': departments,
        'selected_department': department,
        'staff_type': 'hod',
    })


@login_required
@admin_required
def staff_create(request, staff_type):
    if staff_type not in ('teacher', 'guardian', 'hod'):
        messages.error(request, 'Invalid staff type.')
        return redirect('/admin-panel/')

    role_labels = {'teacher': 'Teacher', 'guardian': 'Teacher Guardian', 'hod': 'HOD'}

    if request.method == 'POST':
        form = StaffCreateForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = staff_type
            user.set_password(form.cleaned_data['password'])
            user.created_by = request.user
            user.save()

            log_action(request.user, 'user_create', request,
                       f'Created {staff_type}: {user.full_name}')
            messages.success(request, f'{role_labels[staff_type]} "{user.full_name}" created successfully!')
            return redirect(f'{staff_type}_list')
    else:
        form = StaffCreateForm()

    return render(request, 'staff/staff_create.html', {
        'form': form,
        'staff_type': staff_type,
        'staff_type_label': role_labels[staff_type],
    })


@login_required
@admin_required
def staff_edit(request, staff_type, pk):
    if staff_type not in ('teacher', 'guardian', 'hod'):
        messages.error(request, 'Invalid staff type.')
        return redirect('/admin-panel/')

    role_labels = {'teacher': 'Teacher', 'guardian': 'Teacher Guardian', 'hod': 'HOD'}
    user = get_object_or_404(User, pk=pk, role=staff_type, is_active=True)

    if request.method == 'POST':
        form = StaffEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            updated_user = form.save(commit=False)
            new_password = form.cleaned_data.get('new_password')
            if new_password:
                updated_user.set_password(new_password)
            updated_user.save()

            log_action(request.user, 'user_edit', request,
                       f'Edited {staff_type}: {updated_user.full_name}')
            messages.success(request, f'{role_labels[staff_type]} "{updated_user.full_name}" updated successfully!')
            return redirect(f'{staff_type}_list')
    else:
        form = StaffEditForm(instance=user)

    return render(request, 'staff/staff_edit.html', {
        'form': form,
        'staff_user': user,
        'staff_type': staff_type,
        'staff_type_label': role_labels[staff_type],
    })


@login_required
@admin_required
def staff_delete(request, staff_type, pk):
    if staff_type not in ('teacher', 'guardian', 'hod'):
        messages.error(request, 'Invalid staff type.')
        return redirect('/admin-panel/')

    role_labels = {'teacher': 'Teacher', 'guardian': 'Teacher Guardian', 'hod': 'HOD'}
    user = get_object_or_404(User, pk=pk, role=staff_type, is_active=True)

    if request.method == 'POST':
        user.is_active = False
        user.save()

        log_action(request.user, 'user_delete', request,
                   f'Deleted {staff_type}: {user.full_name}')
        messages.success(request, f'{role_labels[staff_type]} "{user.full_name}" deleted successfully!')

    return redirect(f'{staff_type}_list')


@login_required
@admin_required
def staff_detail(request, staff_type, pk):
    user = get_object_or_404(User, pk=pk, role=staff_type)
    role_labels = {'teacher': 'Teacher', 'guardian': 'Teacher Guardian', 'hod': 'HOD'}

    return render(request, 'staff/staff_detail.html', {
        'staff_user': user,
        'staff_type': staff_type,
        'staff_type_label': role_labels.get(staff_type, staff_type),
    })
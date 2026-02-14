 
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

from .forms import LoginForm, ChangePasswordForm
from .models import User, LoginAttempt, AccountLockout
from .utils import get_client_ip, get_user_agent, log_action


def login_view(request):
    """Handle user login with lockout protection."""
    if request.user.is_authenticated:
        return redirect('/dashboard/')

    form = LoginForm()
    error_message = None

    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            role = form.cleaned_data['role']
            remember_me = form.cleaned_data.get('remember_me', False)

            ip_address = get_client_ip(request)
            user_agent = get_user_agent(request)

            # Check account lockout
            lockout, created = AccountLockout.objects.get_or_create(username=username)

            if lockout.locked_until and lockout.locked_until > timezone.now():
                remaining = (lockout.locked_until - timezone.now()).seconds // 60 + 1
                error_message = f'Account is locked. Try again in {remaining} minutes.'
                LoginAttempt.objects.create(
                    username=username,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    success=False,
                )
                return render(request, 'accounts/login.html', {
                    'form': form,
                    'error_message': error_message,
                })

            # Try to authenticate
            # First try username, then email
            user = authenticate(request, username=username, password=password)

            if user is None:
                # Try email login
                try:
                    user_by_email = User.objects.get(email=username)
                    user = authenticate(request, username=user_by_email.username, password=password)
                except User.DoesNotExist:
                    pass

            if user is not None and user.is_active:
                # Check role matches
                if user.role != role:
                    error_message = f'Invalid role selected. You are not registered as {dict(User.ROLE_CHOICES).get(role, role)}.'
                    LoginAttempt.objects.create(
                        username=username,
                        ip_address=ip_address,
                        user_agent=user_agent,
                        success=False,
                    )
                else:
                    # Successful login
                    login(request, user)

                    # Reset lockout
                    lockout.failed_attempts = 0
                    lockout.locked_until = None
                    lockout.save()

                    # Log success
                    LoginAttempt.objects.create(
                        username=username,
                        ip_address=ip_address,
                        user_agent=user_agent,
                        success=True,
                    )
                    log_action(user, 'login', request, f'Successful login as {role}')

                    # Remember me
                    if not remember_me:
                        request.session.set_expiry(0)  # Browser close

                    request.session['last_activity'] = timezone.now().timestamp()

                    messages.success(request, f'Welcome back, {user.full_name}!')

                    # Redirect based on role
                    role_dashboards = {
                        'admin': '/admin-panel/',
                        'hod': '/hod-panel/',
                        'teacher': '/teacher-panel/',
                        'guardian': '/guardian-panel/',
                    }
                    return redirect(role_dashboards.get(user.role, '/dashboard/'))
            else:
                # Failed login
                lockout.failed_attempts += 1
                max_attempts = getattr(settings, 'MAX_LOGIN_ATTEMPTS', 5)
                lockout_duration = getattr(settings, 'LOCKOUT_DURATION_MINUTES', 15)

                if lockout.failed_attempts >= max_attempts:
                    lockout.locked_until = timezone.now() + timedelta(minutes=lockout_duration)
                    error_message = f'Account locked for {lockout_duration} minutes due to too many failed attempts.'
                else:
                    remaining = max_attempts - lockout.failed_attempts
                    error_message = f'Invalid username or password. {remaining} attempts remaining.'

                lockout.save()

                LoginAttempt.objects.create(
                    username=username,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    success=False,
                )

    return render(request, 'accounts/login.html', {
        'form': form,
        'error_message': error_message,
    })


def logout_view(request):
    """Handle user logout."""
    if request.user.is_authenticated:
        log_action(request.user, 'logout', request)
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('/')


@login_required
def change_password_view(request):
    """Handle password change."""
    form = ChangePasswordForm()

    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)

        if form.is_valid():
            current_password = form.cleaned_data['current_password']
            new_password = form.cleaned_data['new_password']

            if not request.user.check_password(current_password):
                messages.error(request, 'Current password is incorrect.')
            else:
                request.user.set_password(new_password)
                request.user.save()

                log_action(request.user, 'password_change', request)
                messages.success(request, 'Password changed successfully! Please login again.')
                return redirect('/')

    return render(request, 'accounts/change_password.html', {'form': form})


@login_required
def profile_view(request):
    """Show and edit user profile."""
    from .forms import ProfileEditForm

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            log_action(request.user, 'user_edit', request, 'Updated own profile')
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileEditForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def audit_log_view(request):
    """Admin audit log - view all system actions."""
    if request.user.role != 'admin':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('/dashboard/')

    from .models import SecurityLog, LoginAttempt
    from django.core.paginator import Paginator
    from django.db.models import Q

    # Filters
    action_filter = request.GET.get('action', '')
    user_filter = request.GET.get('user', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    search = request.GET.get('search', '')

    logs = SecurityLog.objects.select_related('user').all()

    if action_filter:
        logs = logs.filter(action=action_filter)

    if user_filter:
        logs = logs.filter(user_id=user_filter)

    if date_from:
        logs = logs.filter(timestamp__date__gte=date_from)

    if date_to:
        logs = logs.filter(timestamp__date__lte=date_to)

    if search:
        logs = logs.filter(
            Q(details__icontains=search) |
            Q(user__full_name__icontains=search) |
            Q(user__username__icontains=search)
        )

    # Get filter options
    action_choices = SecurityLog.ACTION_CHOICES
    users = User.objects.filter(is_active=True).order_by('full_name')

    # Login attempts (recent)
    recent_logins = LoginAttempt.objects.all()[:20]

    paginator = Paginator(logs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'accounts/audit_log.html', {
        'page_obj': page_obj,
        'action_choices': action_choices,
        'users': users,
        'action_filter': action_filter,
        'user_filter': user_filter,
        'date_from': date_from,
        'date_to': date_to,
        'search': search,
        'recent_logins': recent_logins,
    })
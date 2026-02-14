 
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(*allowed_roles):
    """Decorator to restrict views to specific roles."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('/')

            if request.user.role not in allowed_roles:
                messages.error(request, 'You do not have permission to access this page.')
                # Redirect to their own dashboard
                role_dashboards = {
                    'admin': '/admin-panel/',
                    'hod': '/hod-panel/',
                    'teacher': '/teacher-panel/',
                    'guardian': '/guardian-panel/',
                }
                return redirect(role_dashboards.get(request.user.role, '/'))

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def admin_required(view_func):
    """Shortcut decorator for admin-only views."""
    return role_required('admin')(view_func)
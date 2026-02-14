from django.utils import timezone
from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings


class SessionTimeoutMiddleware:
    """Auto logout after inactivity."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            last_activity = request.session.get('last_activity')
            timeout = getattr(settings, 'SESSION_TIMEOUT_MINUTES', 30)

            if last_activity:
                elapsed = timezone.now().timestamp() - last_activity
                if elapsed > timeout * 60:
                    from django.contrib.auth import logout
                    logout(request)
                    messages.warning(request, 'Session expired due to inactivity. Please login again.')
                    return redirect('/')

            request.session['last_activity'] = timezone.now().timestamp()

        response = self.get_response(request)
        return response


class SecurityHeadersMiddleware:
    """Add security headers to all responses."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response
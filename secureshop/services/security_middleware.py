import secrets
from functools import wraps
from flask import session, request, abort, current_app, g, redirect, url_for, flash
from secureshop.database import query_db
from secureshop.models import User
from secureshop.services.security_logger import log_security_event

def get_current_user():
    """Fetch current logged-in user or None."""
    if "user" not in g:
        user_id = session.get("user_id")
        if user_id:
            row = query_db("SELECT * FROM users WHERE id = ?", (user_id,), one=True)
            g.user = User.from_row(row) if row else None
        else:
            g.user = None
    return g.user

def generate_csrf_token():
    """Generate or retrieve per-session CSRF token."""
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(32)
    return session["csrf_token"]

def validate_csrf():
    """Verify CSRF token for state-changing browser requests."""
    # Only validate in Secure Mode
    if not current_app.config.get("ENABLE_CSRF", True):
        return  # CSRF checks disabled in vulnerable mode

    if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
        token = request.form.get("csrf_token") or request.headers.get("X-CSRF-Token")
        expected = session.get("csrf_token")

        if not expected or not token or not secrets.compare_digest(expected, token):
            log_security_event(
                "CSRF_VALIDATION_FAILED",
                "WARNING",
                {"method": request.method, "path": request.path}
            )
            abort(400, description="Invalid or missing CSRF token.")

def login_required(f):
    """Decorator requiring an authenticated session."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please sign in to access this page.", "warning")
            return redirect(url_for("auth.login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator requiring administrator privileges."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            flash("Administrator login required.", "warning")
            return redirect(url_for("auth.login", next=request.url))

        user = get_current_user()
        if not user or not user.is_admin:
            log_security_event(
                "AUTHZ_DENIED_ADMIN_ROUTE",
                "WARNING",
                {"attempted_path": request.path, "user_id": session.get("user_id")}
            )
            abort(403, description="Access denied. Administrator privileges required.")
        return f(*args, **kwargs)
    return decorated_function

def apply_security_headers(response):
    """Apply defense-in-depth HTTP security headers in secure mode."""
    if current_app.config.get("ENABLE_SECURITY_HEADERS", True):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:;"
        )
        response.headers["Server"] = "SecureShop-SafeServer"
    else:
        # In vulnerable mode, security headers are omitted to demonstrate A05 Security Misconfiguration
        response.headers["Server"] = "Werkzeug/Debug-Unshielded"
    return response

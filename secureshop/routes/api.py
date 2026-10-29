from flask import Blueprint, jsonify, current_app

api_bp = Blueprint("api", __name__, url_prefix="/api")

@api_bp.route("/health")
def health():
    """Application health and runtime status."""
    return jsonify({
        "status": "UP",
        "app": "SecureShop",
        "mode": current_app.config.get("SECURESHOP_MODE", "secure")
    })

@api_bp.route("/lab/status")
def lab_status():
    """Inspect active security controls and lab mode flags."""
    cfg = current_app.config
    return jsonify({
        "mode": cfg.get("SECURESHOP_MODE"),
        "debug": cfg.get("DEBUG"),
        "csrf_enabled": cfg.get("ENABLE_CSRF", True),
        "security_headers": cfg.get("ENABLE_SECURITY_HEADERS", True),
        "access_control_enforced": cfg.get("ENFORCE_ACCESS_CONTROL", True),
        "safe_search_parameterized": cfg.get("SAFE_SEARCH_ONLY", True),
        "session_cookie_httponly": cfg.get("SESSION_COOKIE_HTTPONLY"),
        "session_cookie_samesite": cfg.get("SESSION_COOKIE_SAMESITE"),
        "max_login_attempts": cfg.get("MAX_LOGIN_ATTEMPTS")
    })

@api_bp.route("/lab/trigger-error")
def trigger_error():
    """Controlled endpoint to demonstrate A05 (Security Misconfiguration).
    In vulnerable mode: Uncaught error displays detailed debug stack trace and environment state.
    In secure mode: Custom error handler catches it and returns sanitized message without trace.
    """
    # Intentional unhandled exception for lab verification
    raise RuntimeError("Lab Simulation: Database connection timeout in internal payment module.")

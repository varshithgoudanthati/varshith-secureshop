import os
from datetime import timedelta

class Config:
    """Base configuration settings for SecureShop."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "secureshop-default-dev-secret-key-2026-safe-acad")
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "instance/secureshop.db")
    SESSION_COOKIE_NAME = "secureshop_session"
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION = 900  # 15 minutes lockout after threshold exceeded
    SERVER_NAME = None

class SecureConfig(Config):
    """Secure production-ready configuration (Default).
    Enforces security headers, parameterized queries, rate limiting, and secure cookies.
    """
    SECURESHOP_MODE = "secure"
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False  # Set to True in HTTPS environments
    ENABLE_CSRF = True
    ENABLE_SECURITY_HEADERS = True
    ENFORCE_ACCESS_CONTROL = True
    SAFE_SEARCH_ONLY = True
    DETAILED_ERROR_PAGES = False

class VulnerableConfig(Config):
    """Educational Vulnerable Lab Configuration.
    Intended strictly for local, isolated security analysis and demonstration.
    Exposes controlled weaknesses across OWASP categories.
    """
    SECURESHOP_MODE = "vulnerable"
    DEBUG = True
    TESTING = False
    SESSION_COOKIE_HTTPONLY = False  # Weak cookie protection (A07)
    SESSION_COOKIE_SAMESITE = None   # Missing SameSite protection (A07)
    SESSION_COOKIE_SECURE = False
    MAX_LOGIN_ATTEMPTS = 999999      # No rate limiting (A07)
    ENABLE_CSRF = False              # CSRF checks disabled
    ENABLE_SECURITY_HEADERS = False  # Missing HTTP security headers (A05)
    ENFORCE_ACCESS_CONTROL = False   # IDOR enabled on order/profile endpoints (A01)
    SAFE_SEARCH_ONLY = False         # SQL injection enabled on product search (A03)
    DETAILED_ERROR_PAGES = True      # Overly informative stack traces on error (A05)

def get_config():
    """Load configuration based on SECURESHOP_MODE environment variable."""
    mode = os.environ.get("SECURESHOP_MODE", "secure").lower().strip()
    if mode == "vulnerable":
        return VulnerableConfig()
    return SecureConfig()

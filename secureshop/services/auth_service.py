import re
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from secureshop.database import get_db, query_db, execute_db
from secureshop.models import User
from secureshop.services.security_logger import log_security_event

def is_ip_locked_out(ip_address: str, username: str) -> bool:
    """Check if the IP or username has exceeded maximum failed login attempts within the lockout window."""
    if not current_app.config.get("MAX_LOGIN_ATTEMPTS") or current_app.config.get("MAX_LOGIN_ATTEMPTS") >= 999999:
        return False  # Throttling disabled in vulnerable mode (A07)

    lockout_seconds = current_app.config.get("LOCKOUT_DURATION", 900)
    max_attempts = current_app.config.get("MAX_LOGIN_ATTEMPTS", 5)
    
    # Query failed attempts in the last lockout_seconds
    threshold_time = datetime.utcnow() - timedelta(seconds=lockout_seconds)
    threshold_str = threshold_time.strftime("%Y-%m-%d %H:%M:%S")

    db = get_db()
    cur = db.execute(
        """
        SELECT COUNT(*) as count FROM login_attempts 
        WHERE (ip_address = ? OR username = ?) 
          AND success = 0 
          AND attempt_time > ?
        """,
        (ip_address, username, threshold_str)
    )
    result = cur.fetchone()
    count = result["count"] if result else 0
    return count >= max_attempts

def record_login_attempt(ip_address: str, username: str, success: bool):
    """Record login attempt in database for audit and rate-limiting purposes."""
    execute_db(
        "INSERT INTO login_attempts (ip_address, username, success) VALUES (?, ?, ?)",
        (ip_address, username, 1 if success else 0)
    )

def authenticate_user(username: str, password: str, ip_address: str):
    """Authenticate user with rate-limiting and secure logging.
    
    Returns:
        (success: bool, message: str, user: Optional[User])
    """
    username = username.strip() if username else ""

    # Rate limiting check (Secure mode defense against A07)
    if is_ip_locked_out(ip_address, username):
        log_security_event(
            "AUTH_LOCKOUT",
            "WARNING",
            {"username": username, "reason": "Max failed attempts exceeded"}
        )
        return False, "Account access temporarily locked due to multiple failed login attempts. Please try again later.", None

    user_row = query_db("SELECT * FROM users WHERE username = ?", (username,), one=True)
    if not user_row:
        record_login_attempt(ip_address, username, success=False)
        log_security_event(
            "AUTH_FAILURE",
            "WARNING",
            {"username": username, "reason": "User not found"}
        )
        return False, "Invalid username or password.", None

    user = User.from_row(user_row)
    if not check_password_hash(user.password_hash, password):
        record_login_attempt(ip_address, username, success=False)
        log_security_event(
            "AUTH_FAILURE",
            "WARNING",
            {"username": username, "user_id": user.id, "reason": "Password mismatch"}
        )
        return False, "Invalid username or password.", None

    # Successful authentication
    record_login_attempt(ip_address, username, success=True)
    log_security_event(
        "AUTH_SUCCESS",
        "INFO",
        {"username": user.username, "is_admin": user.is_admin},
        user_id=user.id
    )
    return True, "Login successful.", user

def register_user(username: str, email: str, password: str, full_name: str, address: str = "", phone: str = "", is_admin: bool = False):
    """Validate and register a new user with secure password hashing."""
    username = username.strip()
    email = email.strip().lower()
    full_name = full_name.strip()

    # Input validations
    if not username or len(username) < 3 or len(username) > 30:
        return False, "Username must be between 3 and 30 characters.", None

    if not re.match(r"^[a-zA-Z0-9_\-]+$", username):
        return False, "Username may only contain letters, numbers, underscores, and hyphens.", None

    if not email or "@" not in email or "." not in email:
        return False, "A valid email address is required.", None

    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters long.", None

    # Check for existing user
    existing = query_db("SELECT id FROM users WHERE username = ? OR email = ?", (username, email), one=True)
    if existing:
        return False, "Username or email is already registered.", None

    # Generate secure password hash
    password_hash = generate_password_hash(password, method="pbkdf2:sha256")

    user_id = execute_db(
        """
        INSERT INTO users (username, email, password_hash, full_name, address, phone, is_admin)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (username, email, password_hash, full_name, address, phone, 1 if is_admin else 0)
    )

    log_security_event(
        "USER_REGISTERED",
        "INFO",
        {"username": username, "email": email, "is_admin": is_admin},
        user_id=user_id
    )

    new_user = User(
        id=user_id,
        username=username,
        email=email,
        password_hash=password_hash,
        full_name=full_name,
        address=address,
        phone=phone,
        is_admin=is_admin
    )
    return True, "Registration successful.", new_user

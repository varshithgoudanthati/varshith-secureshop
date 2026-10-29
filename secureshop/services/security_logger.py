import logging
import os
import json
from datetime import datetime
from flask import request, session, g

logger = logging.getLogger("secureshop_security")
logger.setLevel(logging.INFO)

# File handler for security.log
log_path = os.environ.get("SECURITY_LOG_PATH", "security.log")
handler = logging.FileHandler(log_path, encoding="utf-8")
formatter = logging.Formatter(
    '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "event": %(message)s}'
)
handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(handler)

def log_security_event(event_type: str, severity: str, details: dict, user_id=None):
    """Log security-relevant events safely without secrets.
    
    Args:
        event_type: e.g., 'AUTH_FAILURE', 'AUTHZ_DENIED', 'ADMIN_ACTION'
        severity: 'INFO', 'WARNING', 'CRITICAL'
        details: Dictionary containing contextual telemetry (strictly no passwords or tokens)
        user_id: Optional user identifier
    """
    # Scrub any accidental secrets
    sanitized_details = {}
    for k, v in details.items():
        if any(secret_term in k.lower() for secret_term in ["password", "token", "secret", "card", "cvv"]):
            sanitized_details[k] = "[REDACTED]"
        else:
            sanitized_details[k] = v

    # Extract client IP and path if in request context
    ip = request.remote_addr if request else "N/A"
    endpoint = request.path if request else "N/A"
    
    if user_id is None and "user_id" in session:
        user_id = session.get("user_id")

    payload = {
        "event_type": event_type,
        "severity": severity,
        "user_id": user_id,
        "ip_address": ip,
        "endpoint": endpoint,
        "details": sanitized_details
    }

    # Write to security.log
    if severity == "CRITICAL":
        logger.error(json.dumps(payload))
    elif severity == "WARNING":
        logger.warning(json.dumps(payload))
    else:
        logger.info(json.dumps(payload))

    # Persist in SQLite audit table if database available
    try:
        from secureshop.database import get_db
        db = get_db()
        db.execute(
            """
            INSERT INTO security_events (event_type, severity, user_id, ip_address, endpoint, details)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (event_type, severity, user_id, ip, endpoint, json.dumps(sanitized_details))
        )
        db.commit()
    except Exception:
        # Avoid crashing application if DB context is unavailable (e.g. during CLI or early startup)
        pass

import pytest

def test_security_headers_present_in_secure_mode(secure_client):
    """A05 Defense: Verify essential defense-in-depth HTTP security headers are present in secure mode."""
    res = secure_client.get("/")
    assert res.status_code == 200

    headers = res.headers
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "default-src 'self'" in headers.get("Content-Security-Policy", "")
    assert headers.get("Server") == "SecureShop-SafeServer"

def test_security_headers_missing_in_vulnerable_mode(vulnerable_client):
    """A05 Vulnerability: Demonstrate missing headers and information disclosure in vulnerable lab mode."""
    res = vulnerable_client.get("/")
    assert res.status_code == 200

    headers = res.headers
    assert "X-Frame-Options" not in headers
    assert "Content-Security-Policy" not in headers
    assert "Werkzeug" in headers.get("Server", "")

def test_sanitized_500_error_in_secure_mode(secure_app, secure_client):
    """A05 Defense: Verify application suppresses stack traces on 500 error in secure mode."""
    secure_app.config["TESTING"] = False
    secure_app.config["PROPAGATE_EXCEPTIONS"] = False
    res = secure_client.get("/api/lab/trigger-error")
    assert res.status_code == 500
    assert b"500" in res.data
    # Ensure stack trace information is not disclosed
    assert b"Traceback (most recent call last)" not in res.data
    assert b"RuntimeError: Lab Simulation" not in res.data
    assert b"Hardened Error Response" in res.data

def test_informative_error_in_vulnerable_mode(vulnerable_client):
    """A05 Vulnerability: In vulnerable mode with DEBUG=True, stack traces are intentionally exposed."""
    with pytest.raises(RuntimeError) as exc_info:
        vulnerable_client.get("/api/lab/trigger-error")
    assert "Lab Simulation: Database connection timeout" in str(exc_info.value)

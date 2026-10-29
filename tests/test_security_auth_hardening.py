from tests.conftest import login, get_csrf_token

def test_login_rate_limiting_lockout_in_secure_mode(secure_client):
    """A07 Defense: Verify account lockout after 5 consecutive failed login attempts."""
    # Attempt 5 incorrect logins
    for i in range(5):
        res = login(secure_client, "alice", "WrongPass123!")
        assert res.status_code == 401
        assert b"Invalid username or password" in res.data

    # 6th attempt should be locked out
    lockout_res = login(secure_client, "alice", "WrongPass123!")
    assert lockout_res.status_code == 401
    assert b"temporarily locked" in lockout_res.data

    # Even the correct password is now blocked during the lockout period
    blocked_valid_res = login(secure_client, "alice", "AlicePass123!")
    assert blocked_valid_res.status_code == 401
    assert b"temporarily locked" in blocked_valid_res.data

def test_missing_rate_limiting_in_vulnerable_mode(vulnerable_client):
    """A07 Vulnerability: Demonstrate missing brute-force protection in vulnerable lab mode."""
    # Attempt 8 incorrect logins - none get locked out
    for i in range(8):
        res = login(vulnerable_client, "alice", "WrongPass123!")
        assert res.status_code == 401
        assert b"temporarily locked" not in res.data

    # Valid password still succeeds immediately
    valid_res = login(vulnerable_client, "alice", "AlicePass123!")
    assert valid_res.status_code == 200
    assert b"Welcome back" in valid_res.data

def test_session_cookie_attributes_in_secure_mode(secure_app, secure_client):
    """A07 Defense: Verify session cookie has HttpOnly and SameSite flags enabled."""
    assert secure_app.config["SESSION_COOKIE_HTTPONLY"] is True
    assert secure_app.config["SESSION_COOKIE_SAMESITE"] == "Lax"

    res = secure_client.get("/")
    # Verify cookie configuration on client response
    cookies = res.headers.getlist("Set-Cookie")
    for cookie in cookies:
        if "secureshop_session" in cookie:
            assert "HttpOnly" in cookie

def test_session_cookie_weakness_in_vulnerable_mode(vulnerable_app):
    """A07 Vulnerability: Demonstrate insecure cookie configuration in lab mode."""
    assert vulnerable_app.config["SESSION_COOKIE_HTTPONLY"] is False
    assert vulnerable_app.config["SESSION_COOKIE_SAMESITE"] is None

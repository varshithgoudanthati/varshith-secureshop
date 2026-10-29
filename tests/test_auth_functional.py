from tests.conftest import get_csrf_token, login

def test_login_success_and_logout(secure_client):
    """Test valid user login and subsequent session logout."""
    res = login(secure_client, "alice", "AlicePass123!")
    assert res.status_code == 200
    assert b"Welcome back" in res.data
    assert b"alice" in res.data

    # Logout
    logout_res = secure_client.get("/logout", follow_redirects=True)
    assert logout_res.status_code == 200
    assert b"signed out successfully" in logout_res.data

def test_login_invalid_credentials(secure_client):
    """Test login failure with invalid password."""
    res = login(secure_client, "alice", "WrongPassword!")
    assert res.status_code == 401
    assert b"Invalid username or password" in res.data

def test_login_unknown_user(secure_client):
    """Test login failure with non-existent user."""
    res = login(secure_client, "nonexistent_user", "AnyPassword123!")
    assert res.status_code == 401
    assert b"Invalid username or password" in res.data

def test_user_registration_success(secure_client):
    """Test customer self-registration with valid data."""
    secure_client.get("/register")
    token = get_csrf_token(secure_client)

    data = {
        "csrf_token": token,
        "username": "carol_hacker",
        "email": "carol@example.com",
        "full_name": "Carol Danvers",
        "password": "CarolSecurePass2026!",
        "confirm_password": "CarolSecurePass2026!",
        "address": "77 Beacon St, Boston, MA",
        "phone": "555-0999"
    }

    res = secure_client.post("/register", data=data, follow_redirects=True)
    assert res.status_code == 200
    assert b"Registration successful" in res.data

    # Verify new user can sign in
    login_res = login(secure_client, "carol_hacker", "CarolSecurePass2026!")
    assert login_res.status_code == 200
    assert b"Carol Danvers" in login_res.data

def test_user_registration_mismatched_password(secure_client):
    """Test registration failure when passwords do not match."""
    secure_client.get("/register")
    token = get_csrf_token(secure_client)

    data = {
        "csrf_token": token,
        "username": "dave_user",
        "email": "dave@example.com",
        "full_name": "Dave Miller",
        "password": "Password1!",
        "confirm_password": "DifferentPassword2!",
        "address": "",
        "phone": ""
    }

    res = secure_client.post("/register", data=data, follow_redirects=True)
    assert res.status_code == 400
    assert b"Passwords do not match" in res.data

def test_user_registration_duplicate_username(secure_client):
    """Test registration failure when username already exists."""
    secure_client.get("/register")
    token = get_csrf_token(secure_client)

    data = {
        "csrf_token": token,
        "username": "alice",  # already seeded
        "email": "alice_unique@example.com",
        "full_name": "Duplicate Alice",
        "password": "Password123!",
        "confirm_password": "Password123!",
        "address": "",
        "phone": ""
    }

    res = secure_client.post("/register", data=data, follow_redirects=True)
    assert res.status_code == 400
    assert b"already registered" in res.data

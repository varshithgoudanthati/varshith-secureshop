from tests.conftest import login, get_csrf_token

def test_csrf_protection_rejects_missing_token_in_secure_mode(secure_client):
    """CSRF Defense: Verify state-changing POST request without CSRF token is rejected with HTTP 400."""
    login(secure_client, "alice", "AlicePass123!")

    # Attempt to add item to cart without CSRF token
    res = secure_client.post("/cart/add", data={
        "product_id": 1,
        "quantity": 1
    })
    assert res.status_code == 400
    assert b"Invalid or missing CSRF token" in res.data or b"Bad Request" in res.data

def test_csrf_protection_accepts_valid_token_in_secure_mode(secure_client):
    """CSRF Defense: Verify state-changing POST request with valid CSRF token succeeds."""
    login(secure_client, "alice", "AlicePass123!")

    token = get_csrf_token(secure_client)
    res = secure_client.post("/cart/add", data={
        "csrf_token": token,
        "product_id": 1,
        "quantity": 1
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Product added to your cart" in res.data

def test_csrf_bypassed_in_vulnerable_mode(vulnerable_client):
    """CSRF Vulnerability: In vulnerable mode, requests without tokens are processed."""
    login(vulnerable_client, "alice", "AlicePass123!")

    # Post without CSRF token succeeds in vulnerable mode
    res = vulnerable_client.post("/cart/add", data={
        "product_id": 1,
        "quantity": 1
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Product added to your cart" in res.data

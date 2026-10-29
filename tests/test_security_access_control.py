from tests.conftest import login

def test_idor_order_defense_in_secure_mode(secure_client):
    """A01 Defense: Verify that Alice cannot access Bob's order (Order #3) in secure mode."""
    login(secure_client, "alice", "AlicePass123!")

    # Alice views her own order #1 -> 200 OK
    res_alice_order = secure_client.get("/orders/1")
    assert res_alice_order.status_code == 200
    assert b"ORD-2026-ALICE1" in res_alice_order.data

    # Alice attempts to access Bob's order #3 -> 403 Forbidden
    res_bob_order = secure_client.get("/orders/3")
    assert res_bob_order.status_code == 403
    assert b"Access Denied" in res_bob_order.data or b"Access denied" in res_bob_order.data

def test_idor_order_vulnerability_demonstrated_in_lab_mode(vulnerable_client):
    """A01 Vulnerability: Demonstrate that in vulnerable lab mode, Alice can view Bob's order (Order #3)."""
    login(vulnerable_client, "alice", "AlicePass123!")

    # In vulnerable mode, authorization check is omitted, allowing horizontal privilege escalation
    res = vulnerable_client.get("/orders/3")
    assert res.status_code == 200
    assert b"ORD-2026-BOB001" in res.data
    assert b"Bob Jones" in res.data
    assert b"404 Hacker Ave" in res.data

def test_idor_profile_defense_in_secure_mode(secure_client):
    """A01 Defense: Verify that Alice cannot access Bob's profile (/profile/3) in secure mode."""
    login(secure_client, "alice", "AlicePass123!")

    # Alice attempts to inspect or edit Bob's profile ID 3
    res = secure_client.get("/profile/3")
    assert res.status_code == 403

def test_idor_profile_vulnerability_in_lab_mode(vulnerable_client):
    """A01 Vulnerability: Demonstrate that in vulnerable lab mode, Alice can inspect Bob's profile (/profile/3)."""
    login(vulnerable_client, "alice", "AlicePass123!")

    res = vulnerable_client.get("/profile/3")
    assert res.status_code == 200
    assert b"bob@example.com" in res.data
    assert b"Bob Jones" in res.data

def test_admin_privileged_order_access(secure_client):
    """Verify administrator has legitimate access to inspect orders for support."""
    login(secure_client, "admin", "AdminPass123!")
    res = secure_client.get("/orders/3")
    assert res.status_code == 200
    assert b"ORD-2026-BOB001" in res.data

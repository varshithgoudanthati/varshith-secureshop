from tests.conftest import get_csrf_token, login

def test_admin_dashboard_metrics(secure_client):
    """Test admin dashboard displays operational metrics."""
    login(secure_client, "admin", "AdminPass123!")

    res = secure_client.get("/admin/")
    assert res.status_code == 200
    assert b"Administrative Control Center" in res.data
    assert b"Total Revenue" in res.data
    assert b"Active Products" in res.data
    assert b"Registered Users" in res.data

def test_admin_product_crud_lifecycle(secure_client):
    """Test product creation, updating, and deletion by administrator."""
    login(secure_client, "admin", "AdminPass123!")

    # 1. Create product
    token = get_csrf_token(secure_client)
    create_data = {
        "csrf_token": token,
        "name": "Hardware Security Dongle Test",
        "category": "Security Hardware",
        "price": "79.99",
        "stock": "40",
        "image_url": "/static/img/yubikey.svg",
        "description": "High-assurance hardware token for cryptographic signature testing.",
        "is_active": "1"
    }

    res = secure_client.post("/admin/products/new", data=create_data, follow_redirects=True)
    assert res.status_code == 200
    assert b"created successfully" in res.data
    assert b"Hardware Security Dongle Test" in res.data

    # 2. Edit product (Find its ID by editing)
    # The seeded products are 1..11, so newly created is 12
    token = get_csrf_token(secure_client)
    edit_data = {
        "csrf_token": token,
        "name": "Hardware Security Dongle v2 (Updated)",
        "category": "Security Hardware",
        "price": "89.99",
        "stock": "35",
        "image_url": "/static/img/yubikey.svg",
        "description": "Updated high-assurance hardware token.",
        "is_active": "1"
    }
    edit_res = secure_client.post("/admin/products/12/edit", data=edit_data, follow_redirects=True)
    assert edit_res.status_code == 200
    assert b"updated" in edit_res.data
    assert b"Hardware Security Dongle v2 (Updated)" in edit_res.data

    # 3. Delete product
    token = get_csrf_token(secure_client)
    del_res = secure_client.post("/admin/products/12/delete", data={"csrf_token": token}, follow_redirects=True)
    assert del_res.status_code == 200
    assert b"Product deleted" in del_res.data

def test_admin_user_listing(secure_client):
    """Test admin can view registered users table."""
    login(secure_client, "admin", "AdminPass123!")
    res = secure_client.get("/admin/users")
    assert res.status_code == 200
    assert b"User Directory" in res.data
    assert b"admin@secureshop.local" in res.data
    assert b"alice@example.com" in res.data
    assert b"bob@example.com" in res.data

def test_unauthorized_user_blocked_from_admin(secure_client):
    """Test standard customer cannot access administrative endpoints (403 Forbidden)."""
    # Customer Alice tries to access admin dashboard
    login(secure_client, "alice", "AlicePass123!")

    res = secure_client.get("/admin/")
    assert res.status_code == 403
    assert b"Access Denied" in res.data or b"Administrator privileges required" in res.data

    # Try accessing admin product creation
    create_res = secure_client.get("/admin/products/new")
    assert create_res.status_code == 403

from tests.conftest import get_csrf_token, login

def test_cart_operations(secure_client):
    """Test adding item to cart, updating quantities, and removing items."""
    login(secure_client, "alice", "AlicePass123!")

    # 1. Add product #1 to cart
    token = get_csrf_token(secure_client)
    add_res = secure_client.post("/cart/add", data={
        "csrf_token": token,
        "product_id": 1,
        "quantity": 2
    }, follow_redirects=True)
    assert add_res.status_code == 200
    assert b"Product added to your cart" in add_res.data
    assert b"Hardware Security Key Pro" in add_res.data

    # 2. Update quantity to 4
    token = get_csrf_token(secure_client)
    upd_res = secure_client.post("/cart/update", data={
        "csrf_token": token,
        "product_id": 1,
        "quantity": 4
    }, follow_redirects=True)
    assert upd_res.status_code == 200
    assert b"Cart updated" in upd_res.data

    # 3. Remove product from cart
    token = get_csrf_token(secure_client)
    rem_res = secure_client.post("/cart/remove", data={
        "csrf_token": token,
        "product_id": 1
    }, follow_redirects=True)
    assert rem_res.status_code == 200
    assert b"Your Cart is Currently Empty" in rem_res.data

def test_checkout_simulation(secure_client):
    """Test full checkout simulation from populated cart to order confirmation."""
    login(secure_client, "alice", "AlicePass123!")

    # Add product to cart
    token = get_csrf_token(secure_client)
    secure_client.post("/cart/add", data={
        "csrf_token": token,
        "product_id": 4, # Faraday Bag ($24.99)
        "quantity": 2
    }, follow_redirects=True)

    # Proceed to checkout
    token = get_csrf_token(secure_client)
    checkout_data = {
        "csrf_token": token,
        "shipping_name": "Alice Smith",
        "shipping_address": "101 Cyber Way, Tech City, CA",
        "card_number": "4242 4242 4242 4242",
        "expiry": "12/28",
        "cvv": "123"
    }

    res = secure_client.post("/checkout", data=checkout_data, follow_redirects=True)
    assert res.status_code == 200
    assert b"Simulated Order Confirmed" in res.data
    assert b"ORD-2026-" in res.data

    # Verify cart is now empty
    cart_res = secure_client.get("/cart")
    assert b"Your Cart is Currently Empty" in cart_res.data

def test_order_history_and_profile(secure_client):
    """Test user order history list and profile details update."""
    login(secure_client, "alice", "AlicePass123!")

    # Check Alice's seeded orders
    orders_res = secure_client.get("/orders")
    assert orders_res.status_code == 200
    assert b"ORD-2026-ALICE1" in orders_res.data
    assert b"ORD-2026-ALICE2" in orders_res.data
    # Bob's order should not be in Alice's order history
    assert b"ORD-2026-BOB001" not in orders_res.data

    # Update Alice's profile
    token = get_csrf_token(secure_client)
    profile_data = {
        "csrf_token": token,
        "full_name": "Alice M. Smith",
        "address": "202 New Defense Blvd, Cyber City, CA",
        "phone": "555-4321"
    }
    prof_res = secure_client.post("/profile", data=profile_data, follow_redirects=True)
    assert prof_res.status_code == 200
    assert b"Your profile details have been updated" in prof_res.data
    assert b"Alice M. Smith" in prof_res.data

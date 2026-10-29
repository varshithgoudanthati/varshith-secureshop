import random
import string
from typing import List, Optional, Tuple
from secureshop.database import get_db, query_db, execute_db
from secureshop.models import Order, OrderItem
from secureshop.services.cart_service import get_user_cart, clear_user_cart
from secureshop.services.security_logger import log_security_event

def generate_order_number() -> str:
    """Generate a clean, readable simulated order identifier."""
    random_suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"ORD-2026-{random_suffix}"

def create_order_from_cart(user_id: int, shipping_name: str, shipping_address: str, simulated_card_last4: str = "4242") -> Tuple[bool, str, Optional[Order]]:
    """Simulate order placement from existing cart items.
    
    Academic note: Purely fictional simulation. No real payment processors, cards, or banking APIs used.
    """
    cart = get_user_cart(user_id)
    if not cart["items"]:
        return False, "Your shopping cart is currently empty.", None

    if not shipping_name.strip() or not shipping_address.strip():
        return False, "Shipping name and address are required.", None

    order_num = generate_order_number()
    total = cart["total"]

    order_id = execute_db(
        """
        INSERT INTO orders (order_number, user_id, total_amount, shipping_name, shipping_address, payment_status, order_status)
        VALUES (?, ?, ?, ?, ?, 'Simulated Paid', 'Processing')
        """,
        (order_num, user_id, total, shipping_name.strip(), shipping_address.strip())
    )

    for item in cart["items"]:
        execute_db(
            """
            INSERT INTO order_items (order_id, product_id, product_name, unit_price, quantity, subtotal)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (order_id, item.product_id, item.product_name, item.product_price, item.quantity, item.subtotal)
        )

    # Empty user's cart
    clear_user_cart(user_id)

    log_security_event(
        "ORDER_PLACED",
        "INFO",
        {
            "order_number": order_num,
            "order_id": order_id,
            "total_amount": total,
            "item_count": len(cart["items"])
        },
        user_id=user_id
    )

    created_order = get_order_by_id(order_id, user_id=user_id, is_vulnerable=False, is_admin=True)
    return True, "Order successfully placed!", created_order

def get_user_orders(user_id: int) -> List[Order]:
    """Retrieve all orders placed by the specified user."""
    rows = query_db(
        "SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC",
        (user_id,)
    )
    return [Order.from_row(r) for r in rows]

def get_order_items(order_id: int) -> List[OrderItem]:
    """Retrieve line items for a specific order."""
    rows = query_db(
        "SELECT * FROM order_items WHERE order_id = ? ORDER BY id ASC",
        (order_id,)
    )
    return [
        OrderItem(
            id=r["id"],
            order_id=r["order_id"],
            product_id=r["product_id"],
            product_name=r["product_name"],
            unit_price=float(r["unit_price"]),
            quantity=int(r["quantity"]),
            subtotal=float(r["subtotal"])
        )
        for r in rows
    ]

def get_order_by_id(order_id: int, user_id: Optional[int] = None, is_vulnerable: bool = False, is_admin: bool = False) -> Optional[Order]:
    """Retrieve order details with server-side authorization enforcement.
    
    Demonstrates:
    - In Vulnerable Lab Mode (is_vulnerable=True):
      Ignores user ownership. Any authenticated user can view any other user's order (OWASP A01 IDOR).
    - In Secure Mode (is_vulnerable=False):
      Strictly validates that order.user_id == current_user.id (or admin). Unauthorized attempts return None.
    """
    row = query_db("SELECT * FROM orders WHERE id = ?", (order_id,), one=True)
    if not row:
        return None

    order = Order.from_row(row)

    if not is_vulnerable:
        # SECURE AUTHORIZATION ENFORCEMENT (Defense against A01 Broken Access Control)
        if not is_admin and (user_id is None or order.user_id != user_id):
            log_security_event(
                "AUTHZ_DENIED_IDOR",
                "WARNING",
                {
                    "requested_order_id": order_id,
                    "order_owner_user_id": order.user_id,
                    "attempting_user_id": user_id
                },
                user_id=user_id
            )
            return None

    order.items = get_order_items(order.id)
    return order

def get_all_orders() -> List[Order]:
    """Retrieve all system orders (Admin only)."""
    rows = query_db("SELECT * FROM orders ORDER BY id DESC")
    orders = []
    for r in rows:
        ord_obj = Order.from_row(r)
        ord_obj.items = get_order_items(ord_obj.id)
        orders.append(ord_obj)
    return orders

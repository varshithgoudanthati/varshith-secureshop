from typing import List, Dict, Any
from secureshop.database import get_db, query_db, execute_db
from secureshop.models import CartItem

def get_user_cart(user_id: int) -> Dict[str, Any]:
    """Retrieve full cart summary for a user including subtotals and calculated shipping."""
    db = get_db()
    rows = query_db(
        """
        SELECT c.id, c.user_id, c.product_id, c.quantity,
               p.name as product_name, p.price as product_price, p.image_url as product_image
        FROM cart_items c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ?
        ORDER BY c.id ASC
        """,
        (user_id,)
    )

    items = []
    subtotal = 0.0

    for r in rows:
        item_subtotal = round(float(r["product_price"]) * int(r["quantity"]), 2)
        subtotal += item_subtotal
        items.append(CartItem(
            id=r["id"],
            user_id=r["user_id"],
            product_id=r["product_id"],
            quantity=r["quantity"],
            product_name=r["product_name"],
            product_price=float(r["product_price"]),
            product_image=r["product_image"],
            subtotal=item_subtotal
        ))

    subtotal = round(subtotal, 2)
    # Simulated shipping fee: Free above $100, else $9.99
    shipping = 0.0 if (subtotal >= 100.0 or subtotal == 0.0) else 9.99
    total = round(subtotal + shipping, 2)

    return {
        "items": items,
        "count": sum(item.quantity for item in items),
        "subtotal": subtotal,
        "shipping": shipping,
        "total": total
    }

def add_item_to_cart(user_id: int, product_id: int, quantity: int = 1) -> bool:
    """Add a product to user's cart or increment its quantity."""
    if quantity <= 0:
        return False

    existing = query_db(
        "SELECT id, quantity FROM cart_items WHERE user_id = ? AND product_id = ?",
        (user_id, product_id),
        one=True
    )

    if existing:
        new_qty = existing["quantity"] + quantity
        execute_db(
            "UPDATE cart_items SET quantity = ? WHERE id = ?",
            (new_qty, existing["id"])
        )
    else:
        execute_db(
            "INSERT INTO cart_items (user_id, product_id, quantity) VALUES (?, ?, ?)",
            (user_id, product_id, quantity)
        )
    return True

def update_item_quantity(user_id: int, product_id: int, quantity: int) -> bool:
    """Update item quantity in cart. If 0 or negative, remove item."""
    if quantity <= 0:
        return remove_item_from_cart(user_id, product_id)

    execute_db(
        "UPDATE cart_items SET quantity = ? WHERE user_id = ? AND product_id = ?",
        (quantity, user_id, product_id)
    )
    return True

def remove_item_from_cart(user_id: int, product_id: int) -> bool:
    """Remove a specific product from user's cart."""
    execute_db(
        "DELETE FROM cart_items WHERE user_id = ? AND product_id = ?",
        (user_id, product_id)
    )
    return True

def clear_user_cart(user_id: int):
    """Empty all items from user's shopping cart."""
    execute_db("DELETE FROM cart_items WHERE user_id = ?", (user_id,))

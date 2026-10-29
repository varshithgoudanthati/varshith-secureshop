from flask import Blueprint, render_template, abort, current_app
from secureshop.services.order_service import get_user_orders, get_order_by_id
from secureshop.services.security_middleware import login_required, get_current_user

orders_bp = Blueprint("orders", __name__)

@orders_bp.route("/orders")
@login_required
def history():
    """List orders placed by the current authenticated user."""
    user = get_current_user()
    orders = get_user_orders(user.id)
    return render_template("orders/history.html", orders=orders)

@orders_bp.route("/orders/<int:order_id>")
@login_required
def detail(order_id: int):
    """View order details.
    
    Demonstrates:
    - In Vulnerable Lab Mode (is_vulnerable=True):
      Fails to enforce object ownership (OWASP A01 Broken Access Control / IDOR).
      Any authenticated user can inspect any other customer's order receipt and address.
    - In Secure Mode (is_vulnerable=False):
      Validates server-side that the order belongs to the authenticated user.
      Unauthorized attempts return HTTP 403 Forbidden.
    """
    user = get_current_user()
    is_vulnerable = current_app.config.get("SECURESHOP_MODE") == "vulnerable"

    order = get_order_by_id(
        order_id=order_id,
        user_id=user.id,
        is_vulnerable=is_vulnerable,
        is_admin=user.is_admin
    )

    if not order:
        # If in secure mode and unauthorized or order nonexistent
        abort(403 if not is_vulnerable else 404, description="Access denied or order not found.")

    return render_template("orders/detail.html", order=order)

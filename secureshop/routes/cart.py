from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from secureshop.services.cart_service import (
    get_user_cart,
    add_item_to_cart,
    update_item_quantity,
    remove_item_from_cart,
    clear_user_cart
)
from secureshop.services.order_service import create_order_from_cart
from secureshop.services.security_middleware import login_required, get_current_user

cart_bp = Blueprint("cart", __name__)

@cart_bp.route("/cart")
@login_required
def view_cart():
    """Display current user's shopping cart."""
    user = get_current_user()
    cart_data = get_user_cart(user.id)
    return render_template("cart/cart.html", cart=cart_data)

@cart_bp.route("/cart/add", methods=["POST"])
@login_required
def add():
    """Add item to shopping cart."""
    user = get_current_user()
    try:
        product_id = int(request.form.get("product_id", 0))
        quantity = int(request.form.get("quantity", 1))
    except ValueError:
        flash("Invalid product or quantity specified.", "danger")
        return redirect(url_for("products.catalog"))

    if add_item_to_cart(user.id, product_id, quantity):
        flash("Product added to your cart!", "success")
    else:
        flash("Unable to add product to cart.", "danger")

    return redirect(request.referrer or url_for("cart.view_cart"))

@cart_bp.route("/cart/update", methods=["POST"])
@login_required
def update():
    """Update product quantity in shopping cart."""
    user = get_current_user()
    try:
        product_id = int(request.form.get("product_id", 0))
        quantity = int(request.form.get("quantity", 1))
    except ValueError:
        flash("Invalid quantity value.", "danger")
        return redirect(url_for("cart.view_cart"))

    update_item_quantity(user.id, product_id, quantity)
    flash("Cart updated.", "info")
    return redirect(url_for("cart.view_cart"))

@cart_bp.route("/cart/remove", methods=["POST"])
@login_required
def remove():
    """Remove product from shopping cart."""
    user = get_current_user()
    try:
        product_id = int(request.form.get("product_id", 0))
    except ValueError:
        return redirect(url_for("cart.view_cart"))

    remove_item_from_cart(user.id, product_id)
    flash("Item removed from cart.", "info")
    return redirect(url_for("cart.view_cart"))

@cart_bp.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    """Checkout simulation."""
    user = get_current_user()
    cart_data = get_user_cart(user.id)

    if not cart_data["items"]:
        flash("Your cart is empty. Add items before checking out.", "warning")
        return redirect(url_for("products.catalog"))

    if request.method == "POST":
        shipping_name = request.form.get("shipping_name", "").strip()
        shipping_address = request.form.get("shipping_address", "").strip()
        fake_card = request.form.get("card_number", "").strip()

        if not shipping_name or not shipping_address:
            flash("Please provide complete shipping name and address.", "danger")
            return render_template("cart/checkout.html", cart=cart_data, user=user)

        success, msg, order = create_order_from_cart(
            user_id=user.id,
            shipping_name=shipping_name,
            shipping_address=shipping_address,
            simulated_card_last4=fake_card[-4:] if len(fake_card) >= 4 else "4242"
        )

        if not success:
            flash(msg, "danger")
            return render_template("cart/checkout.html", cart=cart_data, user=user)

        flash("Order successfully placed! Thank you for your simulated purchase.", "success")
        return render_template("cart/order_confirmation.html", order=order)

    return render_template("cart/checkout.html", cart=cart_data, user=user)

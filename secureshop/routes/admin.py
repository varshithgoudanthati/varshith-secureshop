from flask import Blueprint, render_template, request, redirect, url_for, flash
from secureshop.services.security_middleware import admin_required
from secureshop.services.catalog_service import (
    list_products,
    get_product_by_id,
    create_product,
    update_product,
    delete_product,
    get_all_categories
)
from secureshop.services.order_service import get_all_orders
from secureshop.database import query_db
from secureshop.models import User
from secureshop.services.security_logger import log_security_event

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/")
@admin_required
def dashboard():
    """Administrative dashboard displaying system metrics."""
    user_count_row = query_db("SELECT COUNT(*) as c FROM users", one=True)
    product_count_row = query_db("SELECT COUNT(*) as c FROM products", one=True)
    order_count_row = query_db("SELECT COUNT(*) as c FROM orders", one=True)
    revenue_row = query_db("SELECT COALESCE(SUM(total_amount), 0) as s FROM orders", one=True)

    metrics = {
        "users": user_count_row["c"] if user_count_row else 0,
        "products": product_count_row["c"] if product_count_row else 0,
        "orders": order_count_row["c"] if order_count_row else 0,
        "revenue": round(float(revenue_row["s"]), 2) if revenue_row else 0.0
    }

    recent_orders = get_all_orders()[:5]
    recent_logs = query_db("SELECT * FROM security_events ORDER BY id DESC LIMIT 10")

    return render_template(
        "admin/dashboard.html",
        metrics=metrics,
        recent_orders=recent_orders,
        recent_logs=recent_logs
    )

@admin_bp.route("/products")
@admin_required
def products():
    """List all products with administration actions."""
    all_prods = list_products(include_inactive=True, sort_by="all")
    return render_template("admin/products.html", products=all_prods)

@admin_bp.route("/products/new", methods=["GET", "POST"])
@admin_required
def new_product():
    """Create a new product."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "General").strip()
        image_url = request.form.get("image_url", "/static/img/product-default.svg").strip()
        
        try:
            price = float(request.form.get("price", 0.0))
            stock = int(request.form.get("stock", 0))
        except ValueError:
            flash("Invalid price or stock value.", "danger")
            return render_template("admin/product_form.html", product=None, categories=get_all_categories())

        is_active = bool(request.form.get("is_active"))

        prod_id = create_product(name, description, price, category, image_url, stock, is_active)
        log_security_event("ADMIN_PRODUCT_CREATED", "INFO", {"product_id": prod_id, "name": name})
        flash(f"Product '{name}' created successfully.", "success")
        return redirect(url_for("admin.products"))

    return render_template("admin/product_form.html", product=None, categories=get_all_categories())

@admin_bp.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_product(product_id: int):
    """Edit existing product."""
    product = get_product_by_id(product_id)
    if not product:
        flash("Product not found.", "danger")
        return redirect(url_for("admin.products"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "General").strip()
        image_url = request.form.get("image_url", product.image_url).strip()
        
        try:
            price = float(request.form.get("price", product.price))
            stock = int(request.form.get("stock", product.stock))
        except ValueError:
            flash("Invalid numeric value for price or stock.", "danger")
            return render_template("admin/product_form.html", product=product, categories=get_all_categories())

        is_active = bool(request.form.get("is_active"))

        update_product(product_id, name, description, price, category, image_url, stock, is_active)
        log_security_event("ADMIN_PRODUCT_UPDATED", "INFO", {"product_id": product_id, "name": name})
        flash(f"Product '{name}' updated.", "success")
        return redirect(url_for("admin.products"))

    return render_template("admin/product_form.html", product=product, categories=get_all_categories())

@admin_bp.route("/products/<int:product_id>/delete", methods=["POST"])
@admin_required
def remove_product(product_id: int):
    """Delete a product."""
    delete_product(product_id)
    log_security_event("ADMIN_PRODUCT_DELETED", "WARNING", {"product_id": product_id})
    flash("Product deleted.", "info")
    return redirect(url_for("admin.products"))

@admin_bp.route("/users")
@admin_required
def users():
    """User listing and role administration."""
    rows = query_db("SELECT * FROM users ORDER BY id ASC")
    users_list = [User.from_row(r) for r in rows]
    return render_template("admin/users.html", users=users_list)

@admin_bp.route("/logs")
@admin_required
def logs():
    """Display real-time security events audit log."""
    event_logs = query_db("SELECT * FROM security_events ORDER BY id DESC LIMIT 50")
    return render_template("admin/logs.html", logs=event_logs)

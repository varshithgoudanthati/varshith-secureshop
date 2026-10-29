from flask import Blueprint, render_template, request, current_app, abort
from secureshop.services.catalog_service import (
    list_products,
    get_product_by_id,
    get_all_categories,
    search_products
)

products_bp = Blueprint("products", __name__)

@products_bp.route("/")
def index():
    """SecureShop Landing Page."""
    featured = list_products(sort_by="featured")[:6]
    categories = get_all_categories()
    return render_template("index.html", featured_products=featured, categories=categories)

@products_bp.route("/catalog")
def catalog():
    """Full Product Catalog with filters and sorting."""
    category = request.args.get("category", "all")
    sort_by = request.args.get("sort", "featured")

    products = list_products(category=category, sort_by=sort_by)
    categories = get_all_categories()

    return render_template(
        "products/catalog.html",
        products=products,
        categories=categories,
        selected_category=category,
        selected_sort=sort_by,
        search_query=None
    )

@products_bp.route("/products/<int:product_id>")
def detail(product_id: int):
    """Product Detail Page."""
    product = get_product_by_id(product_id)
    if not product or not product.is_active:
        abort(404, description="Product not found.")

    related = [p for p in list_products(category=product.category) if p.id != product.id][:3]
    return render_template("products/detail.html", product=product, related_products=related)

@products_bp.route("/search")
def search():
    """Product search demonstrating A03 SQL Injection in vulnerable mode vs Parameterized queries in secure mode."""
    q = request.args.get("q", "").strip()
    is_vulnerable = current_app.config.get("SECURESHOP_MODE") == "vulnerable"

    categories = get_all_categories()

    try:
        results = search_products(q, is_vulnerable=is_vulnerable)
    except Exception as e:
        # In vulnerable mode, exception exposes query failure / syntax error details (A05)
        if is_vulnerable:
            raise e
        results = []

    return render_template(
        "products/catalog.html",
        products=results,
        categories=categories,
        selected_category="all",
        selected_sort="featured",
        search_query=q,
        is_search=True
    )

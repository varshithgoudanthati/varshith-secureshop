import os
from flask import Flask, render_template, session, g
from secureshop.config import get_config, SecureConfig, VulnerableConfig
from secureshop.database import close_db, init_db, query_db
from secureshop.services.security_middleware import (
    get_current_user,
    generate_csrf_token,
    validate_csrf,
    apply_security_headers
)
from secureshop.services.cart_service import get_user_cart
from secureshop.routes.auth import auth_bp
from secureshop.routes.products import products_bp
from secureshop.routes.cart import cart_bp
from secureshop.routes.orders import orders_bp
from secureshop.routes.admin import admin_bp
from secureshop.routes.api import api_bp

def create_app(config_object=None):
    """Application factory for SecureShop."""
    app = Flask(__name__, instance_relative_config=True)

    if config_object:
        app.config.from_object(config_object)
    else:
        app.config.from_object(get_config())

    # Ensure instance directory exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # Database teardown
    app.teardown_appcontext(close_db)

    # Initialize tables if database does not exist
    with app.app_context():
        init_db()

    # Security Hooks
    app.before_request(validate_csrf)
    app.after_request(apply_security_headers)

    # Context Processors for Jinja Templates
    @app.context_processor
    def inject_global_template_data():
        user = get_current_user()
        cart_count = 0
        if user:
            cart = get_user_cart(user.id)
            cart_count = cart["count"]

        return {
            "current_user": user,
            "cart_count": cart_count,
            "csrf_token": generate_csrf_token(),
            "lab_mode": app.config.get("SECURESHOP_MODE", "secure")
        }

    # Error Handlers
    @app.errorhandler(400)
    def bad_request_error(error):
        return render_template("errors/400.html", error=error), 400

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template("errors/403.html", error=error), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("errors/404.html", error=error), 404

    @app.errorhandler(429)
    def ratelimit_error(error):
        return render_template("errors/429.html", error=error), 429

    @app.errorhandler(500)
    def internal_server_error(error):
        if app.config.get("SECURESHOP_MODE") == "vulnerable" and app.config.get("DEBUG"):
            # In vulnerable mode, allow Flask debug stack trace
            raise error
        return render_template("errors/500.html", error=error), 500

    # Register Blueprints
    app.register_blueprint(products_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    return app

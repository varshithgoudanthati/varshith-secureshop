from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, abort
from secureshop.services.auth_service import authenticate_user, register_user
from secureshop.services.security_middleware import login_required, get_current_user, generate_csrf_token
from secureshop.services.security_logger import log_security_event
from secureshop.database import query_db, execute_db
from secureshop.models import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("products.catalog"))

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        ip = request.remote_addr or "127.0.0.1"
        success, message, user = authenticate_user(username, password, ip)

        if not success:
            flash(message, "danger")
            return render_template("auth/login.html", username=username), 401

        # Successful login: Session Management
        is_vulnerable = current_app.config.get("SECURESHOP_MODE") == "vulnerable"
        if not is_vulnerable:
            # SECURE: Regenerate session to eliminate session fixation risks (A07)
            session.clear()

        session["user_id"] = user.id
        session["username"] = user.username
        session["is_admin"] = user.is_admin
        session["csrf_token"] = generate_csrf_token()
        if remember:
            session.permanent = True

        flash(f"Welcome back, {user.full_name or user.username}!", "success")
        next_url = request.args.get("next")
        if next_url and next_url.startswith("/"):
            return redirect(next_url)
        return redirect(url_for("admin.dashboard") if user.is_admin else url_for("products.catalog"))

    return render_template("auth/login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("products.catalog"))

    if request.method == "POST":
        username = request.form.get("username", "")
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        full_name = request.form.get("full_name", "")
        address = request.form.get("address", "")
        phone = request.form.get("phone", "")

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("auth/register.html", username=username, email=email, full_name=full_name, address=address, phone=phone), 400

        success, message, new_user = register_user(username, email, password, full_name, address, phone, is_admin=False)
        if not success:
            flash(message, "danger")
            return render_template("auth/register.html", username=username, email=email, full_name=full_name, address=address, phone=phone), 400

        flash("Registration successful! You may now sign in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")

@auth_bp.route("/logout")
def logout():
    user_id = session.get("user_id")
    if user_id:
        log_security_event("AUTH_LOGOUT", "INFO", {"user_id": user_id}, user_id=user_id)
    session.clear()
    flash("You have been signed out successfully.", "info")
    return redirect(url_for("products.catalog"))

@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """Secure profile route: Scoped strictly to the session-authenticated user."""
    user = get_current_user()
    if not user:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        address = request.form.get("address", "").strip()
        phone = request.form.get("phone", "").strip()

        execute_db(
            "UPDATE users SET full_name = ?, address = ?, phone = ? WHERE id = ?",
            (full_name, address, phone, user.id)
        )
        flash("Your profile details have been updated.", "success")
        return redirect(url_for("auth.profile"))

    return render_template("profile/profile.html", profile_user=user)

# A01 Broken Access Control Demonstration Endpoint (Lab Mode Only)
@auth_bp.route("/profile/<int:user_id>", methods=["GET", "POST"])
@login_required
def profile_by_id(user_id: int):
    """Vulnerable Profile Route:
    In Vulnerable Mode, allows any authenticated user to view or modify ANY user's profile (IDOR / A01).
    In Secure Mode, enforces server-side ownership check.
    """
    is_vulnerable = current_app.config.get("SECURESHOP_MODE") == "vulnerable"
    current_u = get_current_user()

    if not is_vulnerable:
        # SECURE MODE: Ownership validation
        if not current_u.is_admin and current_u.id != user_id:
            log_security_event(
                "AUTHZ_DENIED_PROFILE_IDOR",
                "WARNING",
                {"attempted_user_id": user_id, "current_user_id": current_u.id},
                user_id=current_u.id
            )
            abort(403, description="Access denied. You cannot access another user's profile.")

    target_row = query_db("SELECT * FROM users WHERE id = ?", (user_id,), one=True)
    if not target_row:
        abort(404, description="User not found.")

    target_user = User.from_row(target_row)

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        address = request.form.get("address", "").strip()
        phone = request.form.get("phone", "").strip()

        execute_db(
            "UPDATE users SET full_name = ?, address = ?, phone = ? WHERE id = ?",
            (full_name, address, phone, target_user.id)
        )
        flash(f"Profile for {target_user.username} has been updated.", "success")
        return redirect(url_for("auth.profile_by_id", user_id=user_id))

    return render_template("profile/profile.html", profile_user=target_user)

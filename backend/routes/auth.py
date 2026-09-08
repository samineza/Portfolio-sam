from flask import Blueprint, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

try:
    from backend.models import get_admin_user_by_email, get_db_connection
except ImportError:
    from models import get_admin_user_by_email, get_db_connection

bp = Blueprint("auth", __name__, url_prefix="/admin")


@bp.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        identifier = (request.form.get("identifier") or "").strip()
        password = request.form.get("password") or ""

        if not identifier or not password:
            return render_template("auth/login.html", error="Please enter your email or username and password.")

        user = get_admin_user_by_email(identifier)
        if not user:
            row = None
            from backend.models import get_db_connection

            conn = get_db_connection()
            row = conn.execute("SELECT * FROM admin_users WHERE username = ?", (identifier,)).fetchone()
            conn.close()
            user = dict(row) if row else None

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["admin_authenticated"] = True
            session["admin_user_id"] = user["id"]
            session["admin_email"] = user["email"]
            return redirect(url_for("admin.dashboard"))

        return render_template("auth/login.html", error="Invalid admin credentials.")

    if session.get("admin_authenticated"):
        return redirect(url_for("admin.dashboard"))
    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login_page"))

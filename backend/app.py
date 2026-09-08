from datetime import datetime
from pathlib import Path

from flask import Flask, redirect, send_from_directory, session, url_for

try:
    from .config import Config
    from .models import get_setting, init_db
except ImportError:
    from config import Config
    from models import get_setting, init_db


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)
    app.static_folder = str(Path(__file__).resolve().parent / "static")

    with app.app_context():
        init_db()

    @app.context_processor
    def inject_defaults():
        return {
            "site_title": "SHEMA",
            "current_year": datetime.utcnow().year,
            "portfolio_owner": get_setting("portfolio_owner", "Ineza Sam Shema"),
            "professional_title": get_setting("professional_title", "Multimedia Producer & Creative Professional"),
            "settings": {
                "email": get_setting("email", "hello@shema.studio"),
                "phone": get_setting("phone", "+250 788 000 000"),
                "location": get_setting("location", "Kigali, Rwanda"),
                "instagram": get_setting("instagram", "https://instagram.com"),
                "youtube": get_setting("youtube", "https://youtube.com"),
                "linkedin": get_setting("linkedin", "https://linkedin.com"),
                "website": get_setting("website", "https://shemastudio.com"),
            },
        }

    @app.before_request
    def set_csrf_token():
        if "csrf_token" not in session:
            import secrets

            session["csrf_token"] = secrets.token_hex(16)

    @app.route("/uploads/<path:filename>")
    def uploaded_file(filename):
        return send_from_directory(Path(app.config["UPLOAD_FOLDER"]).resolve(), filename)

    @app.route("/admin")
    def admin_root():
        if session.get("admin_authenticated"):
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("auth.login_page"))

    try:
        from .routes import admin as admin_bp
        from .routes import auth as auth_bp
        from .routes import public as public_bp
    except ImportError:
        import routes.admin as admin_bp
        import routes.auth as auth_bp
        import routes.public as public_bp

    app.register_blueprint(public_bp.bp)
    app.register_blueprint(auth_bp.bp)
    app.register_blueprint(admin_bp.bp)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

from flask import Blueprint, jsonify, render_template

try:
    from backend.models import get_public_projects
except ImportError:
    from models import get_public_projects

bp = Blueprint("public", __name__)


@bp.route("/")
def home():
    projects = get_public_projects()
    return render_template("public/index.html", projects=projects)


@bp.route("/api/projects")
def api_projects():
    return jsonify({"projects": get_public_projects()})

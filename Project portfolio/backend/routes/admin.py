import os
import uuid
from pathlib import Path

from flask import Blueprint, abort, current_app, jsonify, redirect, render_template, request, session, url_for
from werkzeug.utils import secure_filename

try:
    from backend.models import (
        create_project,
        delete_project,
        delete_project_files,
        get_categories,
        get_dashboard_stats,
        get_project_by_id,
        get_project_media,
        get_recent_projects,
        get_setting,
        list_projects,
        save_project_media,
        set_setting,
        update_project,
    )
except ImportError:
    from models import (
        create_project,
        delete_project,
        delete_project_files,
        get_categories,
        get_dashboard_stats,
        get_project_by_id,
        get_project_media,
        get_recent_projects,
        get_setting,
        list_projects,
        save_project_media,
        set_setting,
        update_project,
    )

bp = Blueprint("admin", __name__, url_prefix="/admin")

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
ALLOWED_VIDEO_EXTENSIONS = {"mp4", "mov", "m4v"}
ALLOWED_MIME = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "video/mp4",
    "video/quicktime",
    "video/x-matroska",
}


def require_admin():
    if not session.get("admin_authenticated"):
        return False
    return True


def secure_storage_path(project_id, media_type):
    upload_root = Path(current_app.config["UPLOAD_FOLDER"]).resolve()
    paths = {
        "image": upload_root / "portfolio" / str(project_id),
        "video": upload_root / "videos" / str(project_id),
        "graphics": upload_root / "graphics" / str(project_id),
        "animations": upload_root / "animations" / str(project_id),
        "photography": upload_root / "photography" / str(project_id),
        "web": upload_root / "web" / str(project_id),
    }
    target = paths.get(media_type, upload_root / "portfolio" / str(project_id))
    target.mkdir(parents=True, exist_ok=True)
    return target


def validate_uploaded_file(file_storage):
    if file_storage is None or file_storage.filename == "":
        raise ValueError("No file selected.")

    filename = secure_filename(file_storage.filename)
    if "." not in filename:
        raise ValueError("File is missing an extension.")

    ext = filename.rsplit(".", 1)[1].lower()
    mime_type = file_storage.mimetype or ""

    if ext not in ALLOWED_EXTENSIONS and ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise ValueError("Unsupported file type.")
    if mime_type and mime_type not in ALLOWED_MIME:
        raise ValueError("File MIME type is not allowed.")

    max_size = int(current_app.config.get("MAX_IMAGE_SIZE", 10 * 1024 * 1024))
    if file_storage.content_length and file_storage.content_length > max_size:
        raise ValueError("File is too large.")

    if file_storage.stream and file_storage.stream.tell() > 0:
        file_storage.stream.seek(0)

    content = file_storage.read(8192)
    file_storage.stream.seek(0)
    if not content:
        raise ValueError("Uploaded file is empty.")

    if ext in {"exe", "php", "py", "js", "html", "htm", "sh", "bat", "cmd"}:
        raise ValueError("Dangerous file type detected.")

    return filename, ext


@bp.before_request
def enforce_admin_auth():
    if request.endpoint and request.endpoint in {"admin.dashboard", "admin.projects", "admin.upload_page", "admin.edit_project_page", "admin.settings_page", "admin.api_projects", "admin.api_project_create", "admin.api_project_update", "admin.api_project_delete", "admin.api_project_toggle", "admin.api_project_bulk"}:
        if not require_admin():
            return redirect(url_for("auth.login_page"))


@bp.route("/dashboard")
def dashboard():
    stats = get_dashboard_stats()
    recent = get_recent_projects(5)
    return render_template("admin/dashboard.html", stats=stats, recent=recent)


@bp.route("/projects")
def projects():
    filters = {
        "search": request.args.get("search", "").strip(),
        "category": request.args.get("category", "").strip(),
        "status": request.args.get("status", "").strip(),
        "sort": request.args.get("sort", "newest"),
    }
    categories = get_categories()
    project_list = list_projects(filters)
    return render_template("admin/projects.html", projects=project_list, categories=categories, filters=filters)


@bp.route("/upload")
def upload_page():
    categories = get_categories()
    return render_template("admin/upload.html", categories=categories)


@bp.route("/settings")
def settings_page():
    settings = {
        "portfolio_owner": get_setting("portfolio_owner", "Ineza Sam Shema"),
        "professional_title": get_setting("professional_title", "Multimedia Producer & Creative Professional"),
        "email": get_setting("email", "hello@shema.studio"),
        "phone": get_setting("phone", "+250 788 000 000"),
        "location": get_setting("location", "Kigali, Rwanda"),
        "instagram": get_setting("instagram", "https://instagram.com"),
        "youtube": get_setting("youtube", "https://youtube.com"),
        "linkedin": get_setting("linkedin", "https://linkedin.com"),
        "website": get_setting("website", "https://shemastudio.com"),
    }
    return render_template("admin/settings.html", settings=settings)


@bp.route("/project/<int:project_id>/edit")
def edit_project_page(project_id):
    project = get_project_by_id(project_id)
    if not project:
        abort(404)
    project["media"] = get_project_media(project_id)
    categories = get_categories()
    return render_template("admin/edit_project.html", project=project, categories=categories)


@bp.route("/api/projects", methods=["GET"])
def api_projects():
    if not require_admin():
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({"projects": list_projects()})


@bp.route("/api/projects", methods=["POST"])
def api_project_create():
    if not require_admin():
        return jsonify({"error": "Unauthorized"}), 401

    title = (request.form.get("title") or "").strip()
    category = (request.form.get("category") or "").strip()
    if not title or not category:
        return jsonify({"error": "Title and category are required."}), 400

    project_id = create_project({
        "title": title,
        "category": category,
        "description": request.form.get("description", ""),
        "client_name": request.form.get("client_name", ""),
        "project_date": request.form.get("project_date", ""),
        "project_url": request.form.get("project_url", ""),
        "status": request.form.get("status", "Draft"),
        "video_url": request.form.get("video_url", ""),
        "youtube_url": request.form.get("youtube_url", ""),
        "vimeo_url": request.form.get("vimeo_url", ""),
        "cover_image": "",
    })

    uploaded_files = []
    files = request.files.getlist("images")
    if files:
        for file_storage in files:
            try:
                filename, ext = validate_uploaded_file(file_storage)
            except ValueError as exc:
                return jsonify({"error": str(exc)}), 400
            safe_name = f"{uuid.uuid4().hex}.{ext}"
            target_dir = secure_storage_path(project_id, "photography")
            target_path = target_dir / safe_name
            file_storage.save(target_path)
            uploaded_files.append({
                "media_type": "image",
                "file_path": str(target_path),
                "alt_text": secure_filename(title),
                "is_cover": False,
            })

    if uploaded_files:
        save_project_media(project_id, uploaded_files)
        cover = request.form.get("cover_image")
        if cover:
            media_list = get_project_media(project_id)
            for item in media_list:
                if item["file_path"].endswith(cover):
                    item_id = item["id"]
                    from backend.models import get_db_connection

                    conn = get_db_connection()
                    conn.execute("UPDATE project_media SET is_cover = 1 WHERE id = ?", (item_id,))
                    conn.execute("UPDATE project_media SET is_cover = 0 WHERE project_id = ? AND id != ?", (project_id, item_id))
                    conn.commit()
                    conn.close()
                    break

        selected_cover = None
        for item in get_project_media(project_id):
            if item["is_cover"]:
                selected_cover = item["file_path"]
                break
        if selected_cover:
            from backend.models import get_db_connection

            conn = get_db_connection()
            conn.execute("UPDATE projects SET cover_image = ? WHERE id = ?", (selected_cover, project_id))
            conn.commit()
            conn.close()

    return jsonify({"success": True, "project_id": project_id, "redirect": url_for("admin.projects")})


@bp.route("/api/projects/<int:project_id>", methods=["PUT"])
def api_project_update(project_id):
    if not require_admin():
        return jsonify({"error": "Unauthorized"}), 401

    project = get_project_by_id(project_id)
    if not project:
        return jsonify({"error": "Project not found."}), 404

    form_data = request.form.to_dict()
    update_project(project_id, {
        "title": form_data.get("title", project["title"]),
        "category": form_data.get("category", project["category"]),
        "description": form_data.get("description", project["description"]),
        "client_name": form_data.get("client_name", project["client_name"]),
        "project_date": form_data.get("project_date", project["project_date"]),
        "project_url": form_data.get("project_url", project["project_url"]),
        "status": form_data.get("status", project["status"]),
        "video_url": form_data.get("video_url", project.get("video_url", "")),
        "youtube_url": form_data.get("youtube_url", project.get("youtube_url", "")),
        "vimeo_url": form_data.get("vimeo_url", project.get("vimeo_url", "")),
        "cover_image": form_data.get("cover_image", project.get("cover_image", "")),
    })

    return jsonify({"success": True})


@bp.route("/api/projects/<int:project_id>", methods=["DELETE"])
def api_project_delete(project_id):
    if not require_admin():
        return jsonify({"error": "Unauthorized"}), 401
    delete_project_files(project_id)
    delete_project(project_id)
    return jsonify({"success": True})


@bp.route("/api/projects/<int:project_id>/toggle", methods=["POST"])
def api_project_toggle(project_id):
    if not require_admin():
        return jsonify({"error": "Unauthorized"}), 401

    project = get_project_by_id(project_id)
    if not project:
        return jsonify({"error": "Project not found."}), 404

    new_status = request.form.get("status", project["status"])
    from backend.models import get_db_connection

    conn = get_db_connection()
    conn.execute("UPDATE projects SET status = ?, updated_at = ? WHERE id = ?", (new_status, __import__("datetime").datetime.utcnow().isoformat(), project_id))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "status": new_status})


@bp.route("/api/settings", methods=["POST"])
def api_settings_save():
    if not require_admin():
        return jsonify({"error": "Unauthorized"}), 401

    payload = request.get_json(silent=True) or {}
    for key, value in payload.items():
        if key in {"portfolio_owner", "professional_title", "email", "phone", "location", "instagram", "youtube", "linkedin", "website"}:
            set_setting(key, str(value))
    return jsonify({"success": True})

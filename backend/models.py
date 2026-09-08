import os
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

from flask import current_app
from werkzeug.security import generate_password_hash

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "backend" / "database" / "portfolio.db"
UPLOAD_ROOT = BASE_DIR / "backend" / "uploads"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    for sub in ["portfolio", "photography", "videos", "graphics", "animations", "web"]:
        (UPLOAD_ROOT / sub).mkdir(parents=True, exist_ok=True)

    conn = get_db_connection()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            slug TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            slug TEXT NOT NULL UNIQUE,
            description TEXT,
            category_id INTEGER,
            client_name TEXT,
            project_date TEXT,
            project_url TEXT,
            cover_image TEXT,
            status TEXT DEFAULT 'Draft' CHECK(status IN ('Draft', 'Published', 'Hidden')),
            video_url TEXT,
            youtube_url TEXT,
            vimeo_url TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(category_id) REFERENCES categories(id)
        );

        CREATE TABLE IF NOT EXISTS project_media (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            media_type TEXT NOT NULL,
            file_path TEXT NOT NULL,
            alt_text TEXT,
            display_order INTEGER DEFAULT 0,
            is_cover INTEGER DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key_name TEXT NOT NULL UNIQUE,
            value TEXT,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    conn.commit()
    conn.close()

    ensure_default_categories()
    ensure_default_admin_user()
    ensure_default_settings()


def ensure_default_categories():
    default_categories = [
        ("Photography", "photography"),
        ("Video Editing", "video-editing"),
        ("Graphic Design", "graphic-design"),
        ("Animation", "animation"),
        ("Motion Graphics", "motion-graphics"),
        ("Web Development", "web-development"),
        ("Multimedia", "multimedia"),
    ]
    conn = get_db_connection()
    for name, slug in default_categories:
        conn.execute(
            "INSERT OR IGNORE INTO categories (name, slug) VALUES (?, ?)",
            (name, slug),
        )
    conn.commit()
    conn.close()


def ensure_default_admin_user():
    from flask import current_app

    email = current_app.config.get("ADMIN_EMAIL", "admin@shema.local")
    password = current_app.config.get("ADMIN_PASSWORD", "SHEMAadmin!2026")
    username = "ineza"
    password_hash = generate_password_hash(password)

    conn = get_db_connection()
    existing = conn.execute(
        "SELECT * FROM admin_users WHERE email = ? OR username = ?",
        (email, username),
    ).fetchone()

    if existing:
        conn.execute(
            "UPDATE admin_users SET username = ?, email = ?, password_hash = ?, updated_at = ? WHERE id = ?",
            (username, email, password_hash, datetime.utcnow().isoformat(), existing["id"]),
        )
    else:
        conn.execute(
            "INSERT INTO admin_users (username, email, password_hash, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (username, email, password_hash, datetime.utcnow().isoformat(), datetime.utcnow().isoformat()),
        )
    conn.commit()
    conn.close()


def ensure_default_settings():
    defaults = {
        "portfolio_owner": "Ineza Sam Shema",
        "professional_title": "Multimedia Producer & Creative Professional",
        "email": "hello@shema.studio",
        "phone": "+250 788 000 000",
        "location": "Kigali, Rwanda",
        "instagram": "https://instagram.com",
        "youtube": "https://youtube.com",
        "linkedin": "https://linkedin.com",
        "website": "https://shemastudio.com",
    }
    conn = get_db_connection()
    for key, value in defaults.items():
        conn.execute(
            "INSERT OR IGNORE INTO settings (key_name, value) VALUES (?, ?)",
            (key, value),
        )
    conn.commit()
    conn.close()


def get_setting(key, default=""):
    conn = get_db_connection()
    row = conn.execute("SELECT value FROM settings WHERE key_name = ?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else default


def set_setting(key, value):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO settings (key_name, value, updated_at) VALUES (?, ?, ?) ON CONFLICT(key_name) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at",
        (key, value, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def slugify(value):
    import re

    value = re.sub(r"[^a-zA-Z0-9\s-]", "", value.lower())
    value = re.sub(r"\s+", "-", value.strip())
    value = re.sub(r"-+", "-", value)
    return value or f"project-{uuid.uuid4().hex[:8]}"


def category_row_to_dict(row):
    return {
        "id": row["id"],
        "name": row["name"],
        "slug": row["slug"],
    }


def project_row_to_dict(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "slug": row["slug"],
        "description": row["description"],
        "category_id": row["category_id"],
        "category": row["category_name"],
        "client_name": row["client_name"],
        "project_date": row["project_date"],
        "project_url": row["project_url"],
        "cover_image": row["cover_image"],
        "status": row["status"],
        "video_url": row["video_url"],
        "youtube_url": row["youtube_url"],
        "vimeo_url": row["vimeo_url"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def get_categories():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM categories ORDER BY id ASC").fetchall()
    conn.close()
    return [category_row_to_dict(row) for row in rows]


def get_category_by_name(name):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM categories WHERE name = ?", (name,)).fetchone()
    conn.close()
    return category_row_to_dict(row) if row else None


def get_or_create_category(name):
    name = name.strip()
    if not name:
        return None
    category = get_category_by_name(name)
    if category:
        return category
    slug = slugify(name)
    conn = get_db_connection()
    cursor = conn.execute("INSERT INTO categories (name, slug) VALUES (?, ?)", (name, slug))
    conn.commit()
    cat_id = cursor.lastrowid
    conn.close()
    return {"id": cat_id, "name": name, "slug": slug}


def get_admin_user_by_email(email):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM admin_users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_project_by_id(project_id):
    conn = get_db_connection()
    row = conn.execute(
        """
        SELECT p.*, c.name as category_name
        FROM projects p
        LEFT JOIN categories c ON c.id = p.category_id
        WHERE p.id = ?
        """,
        (project_id,),
    ).fetchone()
    conn.close()
    return project_row_to_dict(row) if row else None


def get_public_projects():
    conn = get_db_connection()
    rows = conn.execute(
        """
        SELECT p.*, c.name as category_name
        FROM projects p
        LEFT JOIN categories c ON c.id = p.category_id
        WHERE p.status = 'Published'
        ORDER BY p.updated_at DESC, p.id DESC
        """
    ).fetchall()
    conn.close()
    projects = [project_row_to_dict(row) for row in rows]
    for project in projects:
        project["media"] = get_project_media(project["id"])
    return projects


def get_project_media(project_id):
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT * FROM project_media WHERE project_id = ? ORDER BY display_order ASC, id ASC",
        (project_id,),
    ).fetchall()
    conn.close()
    return [
        {
            "id": r["id"],
            "media_type": r["media_type"],
            "file_path": r["file_path"],
            "alt_text": r["alt_text"],
            "display_order": r["display_order"],
            "is_cover": bool(r["is_cover"]),
        }
        for r in rows
    ]


def save_project_media(project_id, media_entries):
    conn = get_db_connection()
    for idx, item in enumerate(media_entries):
        conn.execute(
            """
            INSERT INTO project_media (project_id, media_type, file_path, alt_text, display_order, is_cover, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                project_id,
                item["media_type"],
                item["file_path"],
                item.get("alt_text", ""),
                idx,
                1 if item.get("is_cover") else 0,
                datetime.utcnow().isoformat(),
            ),
        )
    conn.commit()
    conn.close()


def delete_project_files(project_id):
    project = get_project_by_id(project_id)
    if not project:
        return
    media_rows = get_project_media(project_id)
    for item in media_rows:
        path = Path(item["file_path"])
        if path.exists() and path.is_file():
            path.unlink()

    if project.get("cover_image"):
        cover_path = Path(project["cover_image"])
        if cover_path.exists() and cover_path.is_file():
            cover_path.unlink()


def create_project(data):
    category = get_or_create_category(data["category"])
    ts = datetime.utcnow().isoformat()
    slug = slugify(data["title"])
    conn = get_db_connection()
    cursor = conn.execute(
        """
        INSERT INTO projects (
            title, slug, description, category_id, client_name, project_date,
            project_url, cover_image, status, video_url, youtube_url, vimeo_url,
            created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data["title"],
            slug,
            data.get("description", ""),
            category["id"] if category else None,
            data.get("client_name") or "",
            data.get("project_date") or "",
            data.get("project_url") or "",
            data.get("cover_image") or "",
            data.get("status") or "Draft",
            data.get("video_url") or "",
            data.get("youtube_url") or "",
            data.get("vimeo_url") or "",
            ts,
            ts,
        ),
    )
    conn.commit()
    project_id = cursor.lastrowid
    conn.close()
    return project_id


def update_project(project_id, data):
    category = get_or_create_category(data["category"])
    conn = get_db_connection()
    conn.execute(
        """
        UPDATE projects
        SET title = ?, slug = ?, description = ?, category_id = ?, client_name = ?, project_date = ?,
            project_url = ?, cover_image = ?, status = ?, video_url = ?, youtube_url = ?, vimeo_url = ?, updated_at = ?
        WHERE id = ?
        """,
        (
            data["title"],
            slugify(data["title"]),
            data.get("description", ""),
            category["id"] if category else None,
            data.get("client_name") or "",
            data.get("project_date") or "",
            data.get("project_url") or "",
            data.get("cover_image") or "",
            data.get("status") or "Draft",
            data.get("video_url") or "",
            data.get("youtube_url") or "",
            data.get("vimeo_url") or "",
            datetime.utcnow().isoformat(),
            project_id,
        ),
    )
    conn.commit()
    conn.close()


def list_projects(filters=None):
    filters = filters or {}
    conn = get_db_connection()
    query = """
        SELECT p.*, c.name as category_name
        FROM projects p
        LEFT JOIN categories c ON c.id = p.category_id
        WHERE 1=1
    """
    params = []

    if filters.get("category"):
        query += " AND c.name = ?"
        params.append(filters["category"])
    if filters.get("status"):
        query += " AND p.status = ?"
        params.append(filters["status"])
    if filters.get("search"):
        term = f"%{filters['search']}%"
        query += " AND (p.title LIKE ? OR p.client_name LIKE ? OR c.name LIKE ? OR p.description LIKE ?)"
        params.extend([term, term, term, term])

    query += " ORDER BY "
    sort = filters.get("sort", "newest")
    if sort == "oldest":
        query += " p.created_at ASC"
    elif sort == "updated":
        query += " p.updated_at DESC"
    elif sort == "name":
        query += " p.title ASC"
    else:
        query += " p.created_at DESC"

    rows = conn.execute(query, params).fetchall()
    conn.close()
    projects = [project_row_to_dict(row) for row in rows]
    for project in projects:
        project["media"] = get_project_media(project["id"])
    return projects


def count_projects_by_status(status=None):
    conn = get_db_connection()
    if status:
        row = conn.execute("SELECT COUNT(*) AS count FROM projects WHERE status = ?", (status,)).fetchone()
        return row["count"] if row else 0
    row = conn.execute("SELECT COUNT(*) AS count FROM projects").fetchone()
    conn.close()
    return row["count"] if row else 0


def count_projects_by_category(category_name):
    conn = get_db_connection()
    row = conn.execute(
        "SELECT COUNT(*) AS count FROM projects p JOIN categories c ON c.id = p.category_id WHERE c.name = ?",
        (category_name,),
    ).fetchone()
    conn.close()
    return row["count"] if row else 0


def get_dashboard_stats():
    conn = get_db_connection()
    stats = {
        "total": conn.execute("SELECT COUNT(*) AS count FROM projects").fetchone()["count"],
        "photography": conn.execute(
            "SELECT COUNT(*) AS count FROM projects p JOIN categories c ON c.id = p.category_id WHERE c.name = 'Photography'"
        ).fetchone()["count"],
        "videos": conn.execute(
            "SELECT COUNT(*) AS count FROM projects p JOIN categories c ON c.id = p.category_id WHERE c.name = 'Video Editing'"
        ).fetchone()["count"],
        "graphics": conn.execute(
            "SELECT COUNT(*) AS count FROM projects p JOIN categories c ON c.id = p.category_id WHERE c.name = 'Graphic Design'"
        ).fetchone()["count"],
        "animations": conn.execute(
            "SELECT COUNT(*) AS count FROM projects p JOIN categories c ON c.id = p.category_id WHERE c.name = 'Animation'"
        ).fetchone()["count"],
        "published": conn.execute("SELECT COUNT(*) AS count FROM projects WHERE status = 'Published'").fetchone()["count"],
    }
    conn.close()
    return stats


def get_recent_projects(limit=5):
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT p.*, c.name as category_name FROM projects p LEFT JOIN categories c ON c.id = p.category_id ORDER BY updated_at DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [project_row_to_dict(r) for r in rows]


def delete_project(project_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.commit()
    conn.close()


def ensure_project_media_coverage(project_id):
    conn = get_db_connection()
    existing = conn.execute("SELECT * FROM project_media WHERE project_id = ? ORDER BY display_order ASC", (project_id,)).fetchall()
    if not existing:
        conn.close()
        return
    if not any(r["is_cover"] for r in existing):
        first = existing[0]
        conn.execute("UPDATE project_media SET is_cover = 1 WHERE id = ?", (first["id"],))
    conn.commit()
    conn.close()

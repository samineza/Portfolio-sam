import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@shema.local")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "SHEMAadmin!2026")
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # placeholder to avoid unused dependency
    DATABASE_PATH = BASE_DIR / "backend" / "database" / "portfolio.db"
    UPLOAD_FOLDER = BASE_DIR / "backend" / "uploads"
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_IMAGE_SIZE_MB", "10")) * 1024 * 1024
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    MAX_IMAGE_SIZE = int(os.getenv("MAX_IMAGE_SIZE_MB", "10")) * 1024 * 1024

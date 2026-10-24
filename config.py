"""
config.py
---------
Central configuration for the Flask app.
Reads secrets from environment variables (with safe defaults for local dev),
so no secret keys are hard-coded in the source.
"""

import os
import shutil
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    BASE_DIR = BASE_DIR

    # Used to sign session cookies. In production, set this via an
    # environment variable instead of relying on the default.
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

    # SQLite database: on Vercel serverless environments, the filesystem is read-only.
    # We copy the seed DB to /tmp where SQLite can read and write during invocation.
    if os.environ.get("VERCEL"):
        _tmp_db = "/tmp/career.db"
        _src_db = os.path.join(BASE_DIR, "database", "career.db")
        if not os.path.exists(_tmp_db) and os.path.exists(_src_db):
            try:
                shutil.copy2(_src_db, _tmp_db)
            except Exception:
                pass
        _db_path = _tmp_db
    else:
        _db_path = os.path.join(BASE_DIR, "database", "career.db").replace("\\", "/")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{_db_path}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Recommendation algorithm weights (must sum to 1.0).
    WEIGHT_SKILLS = 0.40
    WEIGHT_INTERESTS = 0.30
    WEIGHT_QUIZ = 0.20
    WEIGHT_ACADEMIC = 0.10

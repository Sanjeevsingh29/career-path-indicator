"""
app.py
------
Entry point for the AI-Based Career Recommendation System.

Run with:
    python app.py

First time setup:
    python database/seed.py     (creates tables + sample data + admin login)
"""

from datetime import datetime, timezone
import os

from flask import Flask
from flask_login import LoginManager

from config import Config
from models import db, User

from routes.main import main_bp
from routes.auth import auth_bp
from routes.student import student_bp
from routes.admin import admin_bp


def create_app(config_override=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if config_override:
        app.config.update(config_override)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")

    @app.context_processor
    def inject_globals():
        return {"current_year": datetime.now(timezone.utc).year}

    with app.app_context():
        if not os.environ.get("VERCEL"):
            db_dir = os.path.join(Config.BASE_DIR, "database")
            os.makedirs(db_dir, exist_ok=True)
        db.create_all()
        if not app.config.get("TESTING"):
            try:
                from models import Career
                if not Career.query.first():
                    from database.seed import seed
                    seed(app)
            except Exception:
                pass

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)

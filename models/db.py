"""
db.py
-----
A single shared SQLAlchemy instance. Kept in its own file to avoid
circular imports between app.py and the model files.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

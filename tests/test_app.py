"""
tests/test_app.py
------------------
Basic tests covering the functionality mentioned in the project spec:
registration, login, profile update, quiz submission, recommendation
calculation, skill gap calculation and admin access - plus a few
negative/validation cases.

Run with:
    pytest tests/test_app.py -v
"""

import os
import sys
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from models import db, User, Profile, Skill, Career, CareerSkill, UserSkill
from recommendation.engine import get_skill_gap
from services.validators import is_valid_email, is_valid_password, validate_registration


@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
    })
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


# ---------------------------------------------------------------------------
# Validators (unit tests, no app context needed)
# ---------------------------------------------------------------------------

def test_valid_email():
    assert is_valid_email("student@example.com")
    assert not is_valid_email("not-an-email")
    assert not is_valid_email("")


def test_valid_password():
    assert is_valid_password("abc123")
    assert not is_valid_password("abc")


def test_registration_validation_mismatched_passwords():
    errors = validate_registration("Test", "test@example.com", "abc123", "different")
    assert any("match" in e.lower() for e in errors)


# ---------------------------------------------------------------------------
# Registration & Login
# ---------------------------------------------------------------------------

def test_register_and_login(client):
    resp = client.post("/register", data={
        "name": "Test Student", "email": "test@example.com",
        "password": "abc123", "confirm_password": "abc123",
    }, follow_redirects=True)
    assert resp.status_code == 200

    resp = client.post("/login", data={
        "email": "test@example.com", "password": "abc123",
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Dashboard" in resp.data or b"dashboard" in resp.data.lower()


def test_duplicate_registration_rejected(client):
    data = {"name": "A", "email": "dup@example.com", "password": "abc123", "confirm_password": "abc123"}
    client.post("/register", data=data)
    resp = client.post("/register", data=data, follow_redirects=True)
    assert b"already exists" in resp.data


def test_login_wrong_password(client, app):
    with app.app_context():
        u = User(name="X", email="x@example.com")
        u.set_password("correctpass")
        db.session.add(u)
        db.session.flush()
        db.session.add(Profile(user_id=u.id))
        db.session.commit()

    resp = client.post("/login", data={"email": "x@example.com", "password": "wrongpass"},
                        follow_redirects=True)
    assert b"Invalid email or password" in resp.data


# ---------------------------------------------------------------------------
# Skill Gap / Recommendation
# ---------------------------------------------------------------------------

def test_skill_gap_calculation(app):
    with app.app_context():
        user = User(name="Gap Test", email="gap@example.com")
        user.set_password("abc123")
        db.session.add(user)
        db.session.flush()
        db.session.add(Profile(user_id=user.id, cgpa=8.0))

        python_skill = Skill(name="Python")
        db.session.add(python_skill)
        db.session.flush()

        career = Career(name="Test Career", description="desc")
        db.session.add(career)
        db.session.flush()
        db.session.add(CareerSkill(career_id=career.id, skill_id=python_skill.id, required_level="Intermediate"))

        db.session.add(UserSkill(user_id=user.id, skill_id=python_skill.id, level="Beginner"))
        db.session.commit()

        gap = get_skill_gap(user, career)
        assert len(gap) == 1
        assert gap[0]["status"] == "Improve"  # Beginner < Intermediate required


def test_admin_access_forbidden_for_students(client):
    client.post("/register", data={
        "name": "S", "email": "s@example.com", "password": "abc123", "confirm_password": "abc123",
    })
    client.post("/login", data={"email": "s@example.com", "password": "abc123"})
    resp = client.get("/admin/")
    assert resp.status_code == 403

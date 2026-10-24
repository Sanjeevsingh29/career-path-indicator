"""
models.py
---------
All database tables for the AI-Based Career Recommendation System.

Kept intentionally simple (no deep normalization, no dozens of tables)
so it is easy to explain during a viva.

Skill / Interest levels used throughout the project:
    Beginner (1) -> Basic (2) -> Intermediate (3) -> Advanced (4)
"""

from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from models.db import db


def utcnow():
    return datetime.now(timezone.utc)


# Numeric mapping for skill levels. Kept in one place so the
# recommendation engine and templates both use the same scale.
LEVEL_SCALE = {"Beginner": 1, "Basic": 2, "Intermediate": 3, "Advanced": 4}


# ---------------------------------------------------------------------------
# Users & Profiles
# ---------------------------------------------------------------------------

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=utcnow)

    profile = db.relationship("Profile", backref="user", uselist=False, cascade="all, delete-orphan")
    skills = db.relationship("UserSkill", backref="user", cascade="all, delete-orphan")
    interests = db.relationship("UserInterest", backref="user", cascade="all, delete-orphan")
    results = db.relationship("Result", backref="user", cascade="all, delete-orphan")

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)


class Profile(db.Model):
    __tablename__ = "profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    education = db.Column(db.String(150))     # e.g. "BSc Computer Science"
    college = db.Column(db.String(150))
    year = db.Column(db.String(20))           # e.g. "Final Year"
    cgpa = db.Column(db.Float)                # store on a 0-10 (or 0-4) scale


# ---------------------------------------------------------------------------
# Skills & Interests (master lists + student's own values)
# ---------------------------------------------------------------------------

class Skill(db.Model):
    __tablename__ = "skills"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)


class UserSkill(db.Model):
    __tablename__ = "user_skills"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=False)
    level = db.Column(db.String(20), default="Beginner")  # Beginner/Basic/Intermediate/Advanced

    skill = db.relationship("Skill")


class Interest(db.Model):
    __tablename__ = "interests"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)


class UserInterest(db.Model):
    __tablename__ = "user_interests"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    interest_id = db.Column(db.Integer, db.ForeignKey("interests.id"), nullable=False)

    interest = db.relationship("Interest")


# ---------------------------------------------------------------------------
# Careers
# ---------------------------------------------------------------------------

class Career(db.Model):
    __tablename__ = "careers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text)

    required_skills = db.relationship("CareerSkill", backref="career", cascade="all, delete-orphan")
    related_interests = db.relationship("CareerInterest", backref="career", cascade="all, delete-orphan")
    roadmap_steps = db.relationship("RoadmapStep", backref="career", cascade="all, delete-orphan",
                                     order_by="RoadmapStep.step_number")
    projects = db.relationship("Project", backref="career", cascade="all, delete-orphan")


class CareerSkill(db.Model):
    __tablename__ = "career_skills"
    id = db.Column(db.Integer, primary_key=True)
    career_id = db.Column(db.Integer, db.ForeignKey("careers.id"), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=False)
    required_level = db.Column(db.String(20), default="Intermediate")

    skill = db.relationship("Skill")


class CareerInterest(db.Model):
    __tablename__ = "career_interests"
    id = db.Column(db.Integer, primary_key=True)
    career_id = db.Column(db.Integer, db.ForeignKey("careers.id"), nullable=False)
    interest_id = db.Column(db.Integer, db.ForeignKey("interests.id"), nullable=False)

    interest = db.relationship("Interest")


class RoadmapStep(db.Model):
    __tablename__ = "roadmap_steps"
    id = db.Column(db.Integer, primary_key=True)
    career_id = db.Column(db.Integer, db.ForeignKey("careers.id"), nullable=False)
    step_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(150), nullable=False)
    details = db.Column(db.Text)  # newline separated bullet points


class Project(db.Model):
    __tablename__ = "projects"
    id = db.Column(db.Integer, primary_key=True)
    career_id = db.Column(db.Integer, db.ForeignKey("careers.id"), nullable=False)
    level = db.Column(db.String(20))  # Beginner / Intermediate / Advanced
    title = db.Column(db.String(150), nullable=False)


# ---------------------------------------------------------------------------
# Quiz
# ---------------------------------------------------------------------------

class Question(db.Model):
    __tablename__ = "questions"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50))  # Technical / Personal / WorkPreference

    options = db.relationship("Option", backref="question", cascade="all, delete-orphan")


class Option(db.Model):
    __tablename__ = "options"
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    text = db.Column(db.String(255), nullable=False)

    # Which careers this option gives points to, and how many.
    career_scores = db.relationship("OptionCareerScore", backref="option", cascade="all, delete-orphan")


class OptionCareerScore(db.Model):
    """Each quiz option can add points toward one or more careers.
    This is what makes the quiz scoring simple and fully explainable:
    every point on the results page can be traced back to a specific
    answer the student picked."""
    __tablename__ = "option_career_scores"
    id = db.Column(db.Integer, primary_key=True)
    option_id = db.Column(db.Integer, db.ForeignKey("options.id"), nullable=False)
    career_id = db.Column(db.Integer, db.ForeignKey("careers.id"), nullable=False)
    points = db.Column(db.Integer, default=1)

    career = db.relationship("Career")


class QuizResponse(db.Model):
    """Stores which option a user picked for which question, for one
    assessment attempt (grouped by attempt_id)."""
    __tablename__ = "quiz_responses"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    attempt_id = db.Column(db.String(40), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    option_id = db.Column(db.Integer, db.ForeignKey("options.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow)

    option = db.relationship("Option")


# ---------------------------------------------------------------------------
# Results (final computed recommendations, kept for dashboard history)
# ---------------------------------------------------------------------------

class Result(db.Model):
    __tablename__ = "results"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    career_id = db.Column(db.Integer, db.ForeignKey("careers.id"), nullable=False)
    score = db.Column(db.Float, nullable=False)          # final 0-100 match %
    skill_score = db.Column(db.Float)
    interest_score = db.Column(db.Float)
    quiz_score = db.Column(db.Float)
    academic_score = db.Column(db.Float)
    attempt_id = db.Column(db.String(40))
    created_at = db.Column(db.DateTime, default=utcnow)

    career = db.relationship("Career")

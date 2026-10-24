"""
routes/main.py
---------------
Public pages that don't require login: Home, About, Careers list.
"""

from flask import Blueprint, render_template
from models import Career

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    popular_careers = Career.query.limit(4).all()
    return render_template("home.html", popular_careers=popular_careers)


@main_bp.route("/about")
def about():
    return render_template("about.html")


@main_bp.route("/careers")
def careers():
    all_careers = Career.query.order_by(Career.name).all()
    return render_template("careers.html", careers=all_careers)


@main_bp.route("/careers/<int:career_id>")
def career_public_details(career_id):
    from flask import abort
    career = Career.query.get_or_404(career_id)
    return render_template("career_public.html", career=career)

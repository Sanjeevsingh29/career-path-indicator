"""
routes/admin.py
----------------
A small admin panel. Admins are just User rows with is_admin=True
(created via database/seed.py) - there is no separate admin table,
keeping the database simple.
"""

from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from models import db, User, Career, Question, Option, OptionCareerScore, Skill, CareerSkill

admin_bp = Blueprint("admin", __name__)


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return view(*args, **kwargs)
    return wrapped


@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    stats = {
        "total_students": User.query.filter_by(is_admin=False).count(),
        "total_careers": Career.query.count(),
        "total_questions": Question.query.count(),
    }
    return render_template("admin/dashboard.html", stats=stats)


@admin_bp.route("/users")
@login_required
@admin_required
def manage_users():
    students = User.query.filter_by(is_admin=False).order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", students=students)


@admin_bp.route("/careers")
@login_required
@admin_required
def manage_careers():
    careers = Career.query.order_by(Career.name).all()
    return render_template("admin/careers.html", careers=careers)


@admin_bp.route("/careers/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_career():
    all_skills = Skill.query.order_by(Skill.name).all()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        if not name:
            flash("Career name is required.", "danger")
            return redirect(url_for("admin.add_career"))

        career = Career(name=name, description=description)
        db.session.add(career)
        db.session.flush()

        for sid in request.form.getlist("skill_id"):
            level = request.form.get(f"level_{sid}", "Intermediate")
            db.session.add(CareerSkill(career_id=career.id, skill_id=int(sid), required_level=level))

        db.session.commit()
        flash(f"Career '{name}' added.", "success")
        return redirect(url_for("admin.manage_careers"))

    return render_template("admin/career_form.html", all_skills=all_skills, career=None)


@admin_bp.route("/careers/<int:career_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_career(career_id):
    career = Career.query.get_or_404(career_id)
    all_skills = Skill.query.order_by(Skill.name).all()

    if request.method == "POST":
        career.name = request.form.get("name", "").strip()
        career.description = request.form.get("description", "").strip()

        CareerSkill.query.filter_by(career_id=career.id).delete()
        for sid in request.form.getlist("skill_id"):
            level = request.form.get(f"level_{sid}", "Intermediate")
            db.session.add(CareerSkill(career_id=career.id, skill_id=int(sid), required_level=level))

        db.session.commit()
        flash("Career updated.", "success")
        return redirect(url_for("admin.manage_careers"))

    current_skill_ids = {cs.skill_id for cs in career.required_skills}
    return render_template("admin/career_form.html", all_skills=all_skills, career=career,
                            current_skill_ids=current_skill_ids)


@admin_bp.route("/careers/<int:career_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_career(career_id):
    career = Career.query.get_or_404(career_id)
    db.session.delete(career)
    db.session.commit()
    flash("Career deleted.", "info")
    return redirect(url_for("admin.manage_careers"))


@admin_bp.route("/questions")
@login_required
@admin_required
def manage_questions():
    questions = Question.query.order_by(Question.id).all()
    return render_template("admin/questions.html", questions=questions)


@admin_bp.route("/questions/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_question():
    careers = Career.query.order_by(Career.name).all()
    if request.method == "POST":
        text = request.form.get("text", "").strip()
        category = request.form.get("category", "Technical")
        if not text:
            flash("Question text is required.", "danger")
            return redirect(url_for("admin.add_question"))

        question = Question(text=text, category=category)
        db.session.add(question)
        db.session.flush()

        option_texts = request.form.getlist("option_text")
        for idx, opt_text in enumerate(option_texts):
            if not opt_text.strip():
                continue
            option = Option(question_id=question.id, text=opt_text.strip())
            db.session.add(option)
            db.session.flush()
            for career in careers:
                pts = request.form.get(f"points_{idx}_{career.id}", "0")
                try:
                    pts = int(pts)
                except ValueError:
                    pts = 0
                if pts > 0:
                    db.session.add(OptionCareerScore(option_id=option.id, career_id=career.id, points=pts))

        db.session.commit()
        flash("Question added.", "success")
        return redirect(url_for("admin.manage_questions"))

    return render_template("admin/question_form.html", careers=careers)


@admin_bp.route("/questions/<int:question_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    flash("Question deleted.", "info")
    return redirect(url_for("admin.manage_questions"))

"""
routes/student.py
------------------
Everything a logged-in student can do:
  - Dashboard
  - Profile (view/edit skills, interests, academic info)
  - Career Assessment quiz
  - Results (top 3 recommendations)
  - Career Details (personalized: match %, skill gap, roadmap, projects)
  - Career Comparison (pick 2 careers side by side)
"""

import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user

from models import (
    db, Skill, UserSkill, Interest, UserInterest, Career, Question,
    QuizResponse, Result, LEVEL_SCALE,
)
from recommendation.engine import recommend_careers, get_skill_gap

student_bp = Blueprint("student", __name__)

LEVEL_CHOICES = list(LEVEL_SCALE.keys())


def _weights():
    return {
        "skills": current_app.config["WEIGHT_SKILLS"],
        "interests": current_app.config["WEIGHT_INTERESTS"],
        "quiz": current_app.config["WEIGHT_QUIZ"],
        "academic": current_app.config["WEIGHT_ACADEMIC"],
    }


def _profile_completion(user):
    """Very simple completion percentage used on the dashboard."""
    profile = user.profile
    fields = [
        profile.education if profile else None,
        profile.college if profile else None,
        profile.year if profile else None,
        profile.cgpa if profile else None,
    ]
    filled = sum(1 for f in fields if f not in (None, ""))
    has_skills = len(user.skills) > 0
    has_interests = len(user.interests) > 0
    total_checks = len(fields) + 2
    filled_checks = filled + (1 if has_skills else 0) + (1 if has_interests else 0)
    return round((filled_checks / total_checks) * 100)


@student_bp.route("/dashboard")
@login_required
def dashboard():
    latest_result = (
        Result.query.filter_by(user_id=current_user.id)
        .order_by(Result.created_at.desc())
        .first()
    )
    completion = _profile_completion(current_user)
    return render_template(
        "dashboard.html",
        latest_result=latest_result,
        completion=completion,
        skills_count=len(current_user.skills),
    )


@student_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    all_skills = Skill.query.order_by(Skill.name).all()
    all_interests = Interest.query.order_by(Interest.name).all()

    if request.method == "POST":
        profile = current_user.profile
        profile.education = request.form.get("education", "").strip()
        profile.college = request.form.get("college", "").strip()
        profile.year = request.form.get("year", "").strip()
        cgpa_raw = request.form.get("cgpa", "").strip()
        try:
            profile.cgpa = float(cgpa_raw) if cgpa_raw else None
        except ValueError:
            flash("CGPA must be a number.", "danger")
            return redirect(url_for("student.profile"))

        # Replace skills
        UserSkill.query.filter_by(user_id=current_user.id).delete()
        selected_skill_ids = request.form.getlist("skill_id")
        for sid in selected_skill_ids:
            level = request.form.get(f"level_{sid}", "Beginner")
            db.session.add(UserSkill(user_id=current_user.id, skill_id=int(sid), level=level))

        # Replace interests
        UserInterest.query.filter_by(user_id=current_user.id).delete()
        selected_interest_ids = request.form.getlist("interest_id")
        for iid in selected_interest_ids:
            db.session.add(UserInterest(user_id=current_user.id, interest_id=int(iid)))

        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("student.profile"))

    user_skill_map = {us.skill_id: us.level for us in current_user.skills}
    user_interest_ids = {ui.interest_id for ui in current_user.interests}

    return render_template(
        "profile.html",
        all_skills=all_skills,
        all_interests=all_interests,
        user_skill_map=user_skill_map,
        user_interest_ids=user_interest_ids,
        level_choices=LEVEL_CHOICES,
    )


@student_bp.route("/assessment", methods=["GET", "POST"])
@login_required
def assessment():
    questions = Question.query.order_by(Question.id).all()

    if request.method == "POST":
        attempt_id = uuid.uuid4().hex[:12]
        missing = []
        for q in questions:
            option_id = request.form.get(f"question_{q.id}")
            if not option_id:
                missing.append(q.id)
                continue
            db.session.add(QuizResponse(
                user_id=current_user.id,
                attempt_id=attempt_id,
                question_id=q.id,
                option_id=int(option_id),
            ))

        if missing:
            db.session.rollback()
            flash("Please answer every question before submitting.", "danger")
            return redirect(url_for("student.assessment"))

        db.session.commit()
        return redirect(url_for("student.results", attempt_id=attempt_id))

    return render_template("assessment.html", questions=questions)


@student_bp.route("/results")
@login_required
def latest_results():
    latest = QuizResponse.query.filter_by(user_id=current_user.id).order_by(QuizResponse.created_at.desc()).first()
    if latest:
        return redirect(url_for("student.results", attempt_id=latest.attempt_id))
    flash("Please take the assessment first to see your results.", "info")
    return redirect(url_for("student.assessment"))


@student_bp.route("/results/<attempt_id>")
@login_required
def results(attempt_id):
    quiz_responses = QuizResponse.query.filter_by(
        user_id=current_user.id, attempt_id=attempt_id
    ).all()

    if not quiz_responses:
        flash("No assessment attempt found. Please take the assessment first.", "danger")
        return redirect(url_for("student.assessment"))

    careers = Career.query.all()
    ranked = recommend_careers(current_user, careers, quiz_responses, _weights())

    # Save the results so the dashboard can show recent history.
    for entry in ranked:
        db.session.add(Result(
            user_id=current_user.id,
            career_id=entry["career"].id,
            score=entry["final_score"],
            skill_score=entry["skill_score"],
            interest_score=entry["interest_score"],
            quiz_score=entry["quiz_score"],
            academic_score=entry["academic_score"],
            attempt_id=attempt_id,
        ))
    db.session.commit()

    top3 = ranked[:3]
    return render_template("results.html", top3=top3, all_ranked=ranked, weights=_weights())


@student_bp.route("/career/<int:career_id>")
@login_required
def career_details(career_id):
    career = Career.query.get_or_404(career_id)
    skill_gap = get_skill_gap(current_user, career)
    latest_result = (
        Result.query.filter_by(user_id=current_user.id, career_id=career_id)
        .order_by(Result.created_at.desc())
        .first()
    )
    return render_template("career_details.html", career=career, skill_gap=skill_gap,
                            latest_result=latest_result)


@student_bp.route("/roadmap/<int:career_id>")
@login_required
def roadmap(career_id):
    career = Career.query.get_or_404(career_id)
    return render_template("roadmap.html", career=career)


@student_bp.route("/compare", methods=["GET", "POST"])
@login_required
def compare():
    all_careers = Career.query.order_by(Career.name).all()
    career_a = career_b = None
    gap_a = gap_b = None

    if request.method == "POST":
        id_a = request.form.get("career_a")
        id_b = request.form.get("career_b")
        if id_a and id_b and id_a != id_b:
            career_a = Career.query.get(int(id_a))
            career_b = Career.query.get(int(id_b))
            gap_a = get_skill_gap(current_user, career_a)
            gap_b = get_skill_gap(current_user, career_b)
        else:
            flash("Please select two different careers to compare.", "danger")

    return render_template(
        "compare.html",
        all_careers=all_careers,
        career_a=career_a, career_b=career_b,
        gap_a=gap_a, gap_b=gap_b,
    )

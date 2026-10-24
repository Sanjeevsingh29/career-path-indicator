"""
recommendation/engine.py
-------------------------
This is the "AI" part of the project. It is intentionally a simple,
transparent WEIGHTED SCORING algorithm - not a neural network, not an
LLM, not a black box. Every number it produces can be explained in one
sentence, which is exactly what is needed for a viva.

HOW IT WORKS (explain this during viva):

For every career in the database, we compute four sub-scores out of 100:

1. Skill Score   (40% weight)
   For each skill the career requires, compare the student's level to
   the required level (Beginner < Basic < Intermediate < Advanced).
   score = (student_level / required_level), capped at 100%.
   Average this over all required skills for that career.

2. Interest Score (30% weight)
   Percentage of the career's related interests that the student also
   selected in their profile.

3. Quiz Score (20% weight)
   Every quiz option a student picks adds points toward one or more
   careers (see OptionCareerScore). We sum the points the student
   earned for this career and divide by the maximum points that were
   possible for this career in that quiz, giving a 0-100% score.

4. Academic Score (10% weight)
   Based on the student's CGPA (assumed to be on a 0-10 scale).
   score = (cgpa / 10) * 100

Final Match % = Skill*0.40 + Interest*0.30 + Quiz*0.20 + Academic*0.10

The four weights live in config.py so they can be tuned without
touching this logic, and they are shown to the student on the results
page so nothing is hidden.
"""

from models import LEVEL_SCALE


def _skill_score(user, career):
    """Average of (student level / required level) across every skill
    the career requires. Returns (score_0_100, per_skill_breakdown)."""
    if not career.required_skills:
        return 0.0, []

    # Build a quick lookup: skill_id -> student's level
    user_levels = {us.skill_id: us.level for us in user.skills}

    breakdown = []
    total_ratio = 0.0
    for req in career.required_skills:
        student_level_name = user_levels.get(req.skill_id, None)
        student_points = LEVEL_SCALE.get(student_level_name, 0)
        required_points = LEVEL_SCALE.get(req.required_level, 3)

        ratio = min(student_points / required_points, 1.0) if required_points else 0.0
        total_ratio += ratio

        breakdown.append({
            "skill": req.skill.name,
            "student_level": student_level_name or "None",
            "required_level": req.required_level,
            "ratio": round(ratio * 100, 1),
            "status": "Good" if ratio >= 1.0 else ("Improve" if ratio > 0 else "Missing"),
        })

    score = (total_ratio / len(career.required_skills)) * 100
    return round(score, 1), breakdown


def _interest_score(user, career):
    """Percentage of the career's related interests the student also has."""
    career_interest_ids = {ci.interest_id for ci in career.related_interests}
    if not career_interest_ids:
        return 0.0

    user_interest_ids = {ui.interest_id for ui in user.interests}
    matched = career_interest_ids & user_interest_ids
    return round((len(matched) / len(career_interest_ids)) * 100, 1)


def _quiz_score(career_id, points_earned_by_career, max_points_by_career):
    """Points earned for this career / max possible points for this career."""
    earned = points_earned_by_career.get(career_id, 0)
    maximum = max_points_by_career.get(career_id, 0)
    if maximum == 0:
        return 0.0
    return round((earned / maximum) * 100, 1)


def _academic_score(profile):
    """Simple CGPA based score, assumed on a 0-10 scale. Defaults to a
    neutral 60% if the student hasn't filled this in yet."""
    if profile is None or profile.cgpa is None:
        return 60.0
    cgpa = max(0.0, min(profile.cgpa, 10.0))
    return round((cgpa / 10.0) * 100, 1)


def compute_quiz_points(careers, quiz_responses):
    """Given the student's chosen options for this attempt, calculate:
      - points_earned_by_career: {career_id: points}
      - max_points_by_career: {career_id: max possible points across all questions}
    """
    points_earned = {c.id: 0 for c in careers}

    for response in quiz_responses:
        option = response.option
        for cs in option.career_scores:
            points_earned[cs.career_id] = points_earned.get(cs.career_id, 0) + cs.points

    # Max possible = for every question, take the highest point value
    # offered toward that career, summed across all questions.
    max_points = {c.id: 0 for c in careers}
    all_questions = {r.question_id for r in quiz_responses}
    from models import Question  # local import avoids circular import at module load
    for qid in all_questions:
        question = Question.query.get(qid)
        if not question:
            continue
        for career in careers:
            best = 0
            for opt in question.options:
                for cs in opt.career_scores:
                    if cs.career_id == career.id:
                        best = max(best, cs.points)
            max_points[career.id] += best

    return points_earned, max_points


def recommend_careers(user, careers, quiz_responses, weights):
    """Main entry point. Returns a list of dicts, one per career, sorted
    by final match percentage (highest first)."""

    points_earned, max_points = compute_quiz_points(careers, quiz_responses)
    profile = user.profile

    results = []
    for career in careers:
        skill_pct, skill_breakdown = _skill_score(user, career)
        interest_pct = _interest_score(user, career)
        quiz_pct = _quiz_score(career.id, points_earned, max_points)
        academic_pct = _academic_score(profile)

        final = (
            skill_pct * weights["skills"]
            + interest_pct * weights["interests"]
            + quiz_pct * weights["quiz"]
            + academic_pct * weights["academic"]
        )

        reasons = _build_reasons(skill_breakdown, interest_pct, quiz_pct, academic_pct)

        results.append({
            "career": career,
            "final_score": round(final, 1),
            "skill_score": skill_pct,
            "interest_score": interest_pct,
            "quiz_score": quiz_pct,
            "academic_score": academic_pct,
            "skill_breakdown": skill_breakdown,
            "reasons": reasons,
        })

    results.sort(key=lambda r: r["final_score"], reverse=True)
    return results


def get_skill_gap(user, career):
    """Convenience wrapper used by the Career Details / Skill Gap pages
    when we only need the skill comparison table for ONE career (no
    quiz involved)."""
    _, breakdown = _skill_score(user, career)
    return breakdown


def _build_reasons(skill_breakdown, interest_pct, quiz_pct, academic_pct):
    """Turn the raw numbers into short, human-readable bullet points for
    the 'Why this career?' explanation box."""
    reasons = []

    good_skills = [b["skill"] for b in skill_breakdown if b["status"] == "Good"]
    if good_skills:
        reasons.append(f"Strong skills in: {', '.join(good_skills[:3])}")

    if interest_pct >= 60:
        reasons.append("Your stated interests strongly match this career")
    elif interest_pct >= 30:
        reasons.append("Some of your interests align with this career")

    if quiz_pct >= 60:
        reasons.append("Your assessment answers strongly favored this career")
    elif quiz_pct >= 30:
        reasons.append("Your assessment answers partially favored this career")

    if academic_pct >= 70:
        reasons.append("Your academic background supports this career")

    if not reasons:
        reasons.append("General suitability based on the information provided")

    return reasons

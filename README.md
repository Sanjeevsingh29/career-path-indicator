# Career Compass — AI-Based Career Recommendation System

A Final Year BSc Computer Science project: a Flask web application that
recommends suitable careers to students based on their skills, interests,
academic background, and a short career-assessment quiz.

This is a **student-level** project. The "AI" is a simple, fully
explainable **weighted scoring algorithm** — no neural networks, no LLMs,
no black-box logic. Every score can be traced back to a specific skill,
interest, quiz answer, or CGPA value.

---

## 1. Quick Start

```bash
# 1. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create and seed the database (run once)
python database/seed.py

# 4. Run the app
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

### Demo logins (created by the seed script)
| Role    | Email / Username       | Password    |
|---------|-------------------------|-------------|
| Admin   | `admin@career.local` or `Nanda` | `Nanda`     |
| Student | `student@career.local`  | `student123`|

To reset the database at any time (e.g. after testing), simply delete
`database/career.db` and re-run `python database/seed.py`.

---

## 2. Technology Stack

| Layer          | Technology                          |
|----------------|--------------------------------------|
| Frontend       | HTML5, CSS3, Bootstrap 5, JavaScript |
| Backend        | Python 3, Flask                      |
| Database       | SQLite (via Flask-SQLAlchemy)        |
| Auth           | Flask-Login + Werkzeug password hashing |
| Recommendation | Custom Python weighted-scoring logic |

No React, Docker, microservices, or vector databases — deliberately kept
manageable for a single-student final-year project.

---

## 3. Recommendation Algorithm (explain this in viva)

For every career, four sub-scores (0–100) are calculated:

| Factor              | Weight | How it's calculated |
|----------------------|--------|----------------------|
| **Skill Match**       | 40%    | For each skill the career requires, compare your level (Beginner→Advanced) to the required level. Average the ratios across all required skills. |
| **Interest Match**    | 30%    | % of the career's related interests that you also selected in your profile. |
| **Quiz Score**        | 20%    | Points you earned toward that career from your quiz answers, divided by the maximum points possible for that career. |
| **Academic Score**    | 10%    | Based on your CGPA (assumed 0–10 scale): `(cgpa / 10) * 100`. |

```
Final Match % = Skill*0.40 + Interest*0.30 + Quiz*0.20 + Academic*0.10
```

The weights live in `config.py` so they can be tuned without touching
the algorithm itself. See `recommendation/engine.py` for the full,
heavily-commented implementation.

---

## 4. Project Structure

```
career_project/
│
├── app.py                  # Flask app factory / entry point
├── config.py                # App configuration (secret key, DB, weights)
├── requirements.txt
│
├── models/                  # SQLAlchemy models (db.py, models.py)
├── routes/                  # Blueprints: main, auth, student, admin
├── recommendation/          # The scoring algorithm (engine.py)
├── services/                 # Small helpers (form validators)
│
├── templates/               # Jinja2 HTML templates
│   ├── base.html, student_base.html
│   ├── home.html, about.html, careers.html, career_public.html
│   ├── login.html, register.html
│   ├── dashboard.html, profile.html, assessment.html, results.html
│   ├── career_details.html, roadmap.html, compare.html
│   └── admin/                # Admin panel templates
│
├── static/
│   ├── css/style.css         # Custom navy/amber theme (Bootstrap base)
│   ├── js/
│   └── images/
│
├── database/
│   ├── seed.py                # Creates tables + sample data
│   └── career.db              # SQLite database (generated)
│
├── tests/
│   └── test_app.py            # Pytest suite
│
└── README.md
```

---

## 5. Database Tables

`users`, `profiles`, `skills`, `user_skills`, `interests`, `user_interests`,
`careers`, `career_skills`, `career_interests`, `roadmap_steps`, `projects`,
`questions`, `options`, `option_career_scores`, `quiz_responses`, `results`.

Kept as a single, simple relational schema — no unnecessary normalization.

---

## 6. Running Tests

```bash
pytest tests/test_app.py -v
```

Covers: registration, duplicate-email rejection, login (success/failure),
skill-gap calculation, and admin-access restriction.

---

## 7. Important Limitations (shown in-app)

Career recommendations are **guidance only**, based on the information the
student provides. They are **not guaranteed predictions**. The system does
not claim to "know your perfect career" — it suggests suitable options
based on skills, interests, and assessment results.

---

## 8. Common Viva Questions — Quick Answers

- **Why Flask, not Django?** Flask is lightweight and lets you see exactly
  how routing, sessions, and the ORM work — easier to explain end-to-end.
- **Why SQLite?** Zero configuration, file-based, perfect for a
  single-user academic project; the schema would port to
  PostgreSQL/MySQL with almost no code changes.
- **How is the score explainable?** Every sub-score (skill/interest/quiz/
  academic) is stored and shown on the Results page, along with the
  weights used, so a student (or examiner) can verify the math by hand.
- **What's the biggest limitation?** The system only knows what the
  student tells it — inaccurate self-reported skill levels or an
  incomplete quiz will directly affect the recommendation quality.
- **Future scope?** Real ML-based skill inference from GitHub/resume
  parsing, more careers, adaptive quizzes, and email-based roadmap
  reminders.

"""
database/seed.py
-----------------
Run this ONCE to create the SQLite database and fill it with realistic
sample data (skills, interests, careers, roadmap, projects, quiz
questions, an admin account and a demo student account).

Usage:
    python database/seed.py
"""

import os
import sys

# Allow running this script directly (python database/seed.py)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models import (
    db, User, Profile, Skill, Interest, Career, CareerSkill, CareerInterest,
    RoadmapStep, Project, Question, Option, OptionCareerScore,
)

SKILLS = [
    "Python", "Java", "JavaScript", "HTML/CSS", "SQL", "Git",
    "Data Analysis", "Statistics", "Machine Learning", "UI/UX Design",
    "Figma", "Mobile Development (Flutter/React Native)", "Cloud Basics (AWS/Azure)",
    "Networking", "Software Testing", "Problem Solving",
]

INTERESTS = [
    "Programming", "Databases", "Logical Problem Solving", "Designing Interfaces",
    "Working with Numbers/Data", "Learning New Technologies", "Building Apps",
    "Analyzing Trends", "Automating Tasks", "Cloud & Infrastructure",
]

# Each career: name, description, {skill: required_level}, [interests],
# roadmap steps [(title, [bullets])], projects {level: [titles]}
CAREERS = [
    {
        "name": "Software Developer",
        "description": "Designs, builds and maintains software applications using programming "
                        "languages, data structures and problem-solving skills.",
        "skills": {"Python": "Intermediate", "Java": "Basic", "Git": "Basic",
                   "SQL": "Basic", "Problem Solving": "Intermediate"},
        "interests": ["Programming", "Logical Problem Solving", "Building Apps"],
        "roadmap": [
            ("Programming Basics", ["Learn Python or Java", "Practice problem solving"]),
            ("Data Structures", ["Arrays, Lists, Stacks, Queues", "Basic algorithms"]),
            ("Database Basics", ["SQL fundamentals", "Database design basics"]),
            ("Build Projects", ["Build 2-3 small projects", "Upload projects to GitHub"]),
        ],
        "projects": {
            "Beginner": ["To-Do Application"],
            "Intermediate": ["Library Management System"],
            "Advanced": ["E-Commerce Website"],
        },
    },
    {
        "name": "Web Developer",
        "description": "Builds websites and web applications, working on front-end interfaces "
                        "and/or back-end logic.",
        "skills": {"HTML/CSS": "Intermediate", "JavaScript": "Intermediate",
                   "Git": "Basic", "SQL": "Basic"},
        "interests": ["Programming", "Designing Interfaces", "Building Apps"],
        "roadmap": [
            ("Web Basics", ["HTML5 and CSS3", "Responsive design"]),
            ("JavaScript", ["DOM manipulation", "Basic JS frameworks"]),
            ("Backend Basics", ["Flask or Node.js basics", "REST APIs"]),
            ("Build Projects", ["Build a portfolio website", "Build a small full-stack app"]),
        ],
        "projects": {
            "Beginner": ["Personal Portfolio Website"],
            "Intermediate": ["Blog Platform with Login"],
            "Advanced": ["Full-stack Booking System"],
        },
    },
    {
        "name": "Data Analyst",
        "description": "Collects, cleans and analyzes data to find trends and support "
                        "business decisions using statistics and visualization tools.",
        "skills": {"SQL": "Intermediate", "Data Analysis": "Intermediate",
                   "Statistics": "Basic", "Python": "Basic"},
        "interests": ["Working with Numbers/Data", "Analyzing Trends", "Databases"],
        "roadmap": [
            ("Excel & SQL", ["Spreadsheet analysis", "SQL queries"]),
            ("Statistics", ["Descriptive statistics", "Basic probability"]),
            ("Python for Data", ["Pandas basics", "Data cleaning"]),
            ("Visualization", ["Build dashboards", "Present insights"]),
        ],
        "projects": {
            "Beginner": ["Sales Data Analysis"],
            "Intermediate": ["Student Performance Dashboard"],
            "Advanced": ["Business Data Dashboard"],
        },
    },
    {
        "name": "Data Scientist",
        "description": "Uses statistics, programming and machine learning to extract insights "
                        "and build predictive models from data.",
        "skills": {"Python": "Intermediate", "Statistics": "Intermediate",
                   "Machine Learning": "Basic", "SQL": "Basic"},
        "interests": ["Working with Numbers/Data", "Learning New Technologies", "Analyzing Trends"],
        "roadmap": [
            ("Foundations", ["Python + Statistics basics", "Data handling with Pandas"]),
            ("Machine Learning Basics", ["Regression & Classification", "Scikit-learn basics"]),
            ("Practice", ["Kaggle beginner datasets", "Model evaluation basics"]),
            ("Projects", ["Build 1-2 ML mini projects", "Document your process"]),
        ],
        "projects": {
            "Beginner": ["House Price Prediction"],
            "Intermediate": ["Customer Churn Prediction"],
            "Advanced": ["Recommendation System Prototype"],
        },
    },
    {
        "name": "AI/ML Engineer",
        "description": "Builds and deploys machine learning models and AI-driven features "
                        "into real applications.",
        "skills": {"Python": "Advanced", "Machine Learning": "Intermediate",
                   "Statistics": "Basic", "Git": "Basic"},
        "interests": ["Learning New Technologies", "Programming", "Working with Numbers/Data"],
        "roadmap": [
            ("Programming + Math", ["Strong Python", "Linear algebra basics"]),
            ("ML Fundamentals", ["Supervised/unsupervised learning", "Model tuning basics"]),
            ("Deployment Basics", ["Save/load models", "Simple Flask API for a model"]),
            ("Projects", ["Build an end-to-end ML mini project"]),
        ],
        "projects": {
            "Beginner": ["Spam Email Classifier"],
            "Intermediate": ["Image Classification App"],
            "Advanced": ["ML Model Deployed as a Web API"],
        },
    },
    {
        "name": "UI/UX Designer",
        "description": "Designs user interfaces and experiences that are easy, pleasant and "
                        "efficient to use.",
        "skills": {"UI/UX Design": "Intermediate", "Figma": "Intermediate", "HTML/CSS": "Basic"},
        "interests": ["Designing Interfaces", "Building Apps"],
        "roadmap": [
            ("Design Basics", ["Color, typography, layout", "Design principles"]),
            ("Tools", ["Learn Figma", "Wireframing and prototyping"]),
            ("User Research", ["Basic usability testing", "User personas"]),
            ("Portfolio", ["Design 2-3 case studies", "Build a design portfolio"]),
        ],
        "projects": {
            "Beginner": ["Redesign a Simple App Screen"],
            "Intermediate": ["Mobile App UI Kit"],
            "Advanced": ["Full Product Design Case Study"],
        },
    },
    {
        "name": "Mobile App Developer",
        "description": "Builds mobile applications for Android/iOS using cross-platform or "
                        "native frameworks.",
        "skills": {"Mobile Development (Flutter/React Native)": "Intermediate",
                   "JavaScript": "Basic", "Git": "Basic"},
        "interests": ["Building Apps", "Programming"],
        "roadmap": [
            ("Basics", ["Learn Flutter or React Native basics", "App layout concepts"]),
            ("State & Navigation", ["State management basics", "Multi-screen navigation"]),
            ("APIs", ["Connect app to a REST API"]),
            ("Projects", ["Build and publish a demo app"]),
        ],
        "projects": {
            "Beginner": ["Notes Taking App"],
            "Intermediate": ["Weather App with API"],
            "Advanced": ["E-commerce Mobile App"],
        },
    },
    {
        "name": "Cloud Engineer",
        "description": "Sets up, manages and secures cloud infrastructure and deployments.",
        "skills": {"Cloud Basics (AWS/Azure)": "Intermediate", "Networking": "Basic", "Git": "Basic"},
        "interests": ["Cloud & Infrastructure", "Automating Tasks"],
        "roadmap": [
            ("Cloud Basics", ["Core AWS/Azure services", "Cloud fundamentals certification prep"]),
            ("Networking", ["Basic networking concepts", "Security groups/firewalls"]),
            ("Deployment", ["Deploy a simple app to the cloud"]),
            ("Automation", ["Basic scripting for automation"]),
        ],
        "projects": {
            "Beginner": ["Host a Static Website on Cloud"],
            "Intermediate": ["Deploy a Flask App to the Cloud"],
            "Advanced": ["Set up a Simple CI/CD Pipeline"],
        },
    },
    {
        "name": "Database Administrator",
        "description": "Manages, secures and optimizes databases that store an organization's "
                        "data.",
        "skills": {"SQL": "Advanced", "Data Analysis": "Basic", "Networking": "Basic"},
        "interests": ["Databases", "Working with Numbers/Data"],
        "roadmap": [
            ("SQL Mastery", ["Advanced SQL queries", "Indexes and optimization"]),
            ("Database Design", ["Normalization", "ER modeling"]),
            ("Administration", ["Backups and recovery basics", "User permissions"]),
            ("Practice", ["Manage a sample production-like database"]),
        ],
        "projects": {
            "Beginner": ["Design a Database for a Small Shop"],
            "Intermediate": ["Optimize Slow SQL Queries Project"],
            "Advanced": ["Backup & Recovery Simulation"],
        },
    },
    {
        "name": "QA/Software Tester",
        "description": "Tests software to find bugs and ensure it works correctly before "
                        "release.",
        "skills": {"Software Testing": "Intermediate", "SQL": "Basic", "Problem Solving": "Basic"},
        "interests": ["Logical Problem Solving", "Programming"],
        "roadmap": [
            ("Testing Basics", ["Manual testing fundamentals", "Writing test cases"]),
            ("Bug Tracking", ["Using a bug tracking tool", "Reporting bugs clearly"]),
            ("Automation Basics", ["Basic automated testing concepts"]),
            ("Practice", ["Test a real small application thoroughly"]),
        ],
        "projects": {
            "Beginner": ["Write Test Cases for a To-Do App"],
            "Intermediate": ["Manual Testing Report for a Web App"],
            "Advanced": ["Basic Automated Test Suite"],
        },
    },
]

# Quiz questions. Each option lists which careers it awards points to.
QUESTIONS = [
    ("Do you enjoy writing computer programs?", "Technical", [
        ("Yes, I enjoy it a lot", {"Software Developer": 3, "Web Developer": 2, "AI/ML Engineer": 2}),
        ("Somewhat, depends on the problem", {"Software Developer": 1, "QA/Software Tester": 1}),
        ("Not really", {"UI/UX Designer": 1}),
    ]),
    ("Do you enjoy working with databases and structured data?", "Technical", [
        ("Yes, I like organizing and querying data", {"Database Administrator": 3, "Data Analyst": 2}),
        ("A little", {"Data Analyst": 1}),
        ("Not particularly", {}),
    ]),
    ("Do you like solving logical/mathematical problems?", "Technical", [
        ("Yes, I enjoy logic puzzles and math", {"Data Scientist": 2, "AI/ML Engineer": 2, "Software Developer": 1}),
        ("Sometimes", {"QA/Software Tester": 1}),
        ("Not my favorite", {}),
    ]),
    ("Do you enjoy designing how an app or website looks and feels?", "Personal", [
        ("Yes, visual design excites me", {"UI/UX Designer": 3}),
        ("A little interested", {"UI/UX Designer": 1, "Web Developer": 1}),
        ("Not interested", {}),
    ]),
    ("Do you enjoy working with numbers, charts and statistics?", "Personal", [
        ("Yes, a lot", {"Data Analyst": 3, "Data Scientist": 2}),
        ("Somewhat", {"Data Analyst": 1}),
        ("Not really", {}),
    ]),
    ("Do you enjoy learning new technologies and tools?", "Personal", [
        ("Yes, I love exploring new tech", {"AI/ML Engineer": 2, "Cloud Engineer": 2, "Mobile App Developer": 1}),
        ("Sometimes, if needed", {"Software Developer": 1}),
        ("I prefer sticking to what I know", {}),
    ]),
    ("Do you prefer coding or designing interfaces?", "WorkPreference", [
        ("Coding", {"Software Developer": 2, "Web Developer": 1, "Mobile App Developer": 1}),
        ("Designing", {"UI/UX Designer": 3}),
        ("Both equally", {"Web Developer": 1, "UI/UX Designer": 1}),
    ]),
    ("Do you prefer analytical work over creative work?", "WorkPreference", [
        ("Yes, I prefer analytical work", {"Data Analyst": 2, "Data Scientist": 2, "Database Administrator": 1}),
        ("I prefer creative work", {"UI/UX Designer": 2}),
        ("I enjoy a mix of both", {"Software Developer": 1}),
    ]),
    ("Do you enjoy building mobile apps?", "Technical", [
        ("Yes, definitely", {"Mobile App Developer": 3}),
        ("Maybe, haven't tried much", {"Mobile App Developer": 1}),
        ("Not interested", {}),
    ]),
    ("Do you enjoy working with cloud platforms and servers?", "Technical", [
        ("Yes, infrastructure interests me", {"Cloud Engineer": 3}),
        ("A little curious", {"Cloud Engineer": 1}),
        ("Not really", {}),
    ]),
    ("Do you enjoy finding bugs and testing how things break?", "Personal", [
        ("Yes, I like finding issues", {"QA/Software Tester": 3}),
        ("Sometimes", {"QA/Software Tester": 1}),
        ("Not really", {}),
    ]),
    ("Do you enjoy training models to make predictions?", "Technical", [
        ("Yes, machine learning interests me", {"AI/ML Engineer": 3, "Data Scientist": 2}),
        ("A little curious", {"Data Scientist": 1}),
        ("Not really", {}),
    ]),
    ("Do you prefer front-end (visuals) or back-end (logic) work?", "WorkPreference", [
        ("Front-end", {"Web Developer": 2, "UI/UX Designer": 1}),
        ("Back-end", {"Software Developer": 2, "Database Administrator": 1}),
        ("Both / Full-stack", {"Web Developer": 2, "Software Developer": 1}),
    ]),
    ("Do you enjoy presenting insights and findings to others?", "Personal", [
        ("Yes, I enjoy presenting data-driven insights", {"Data Analyst": 2, "Data Scientist": 1}),
        ("Sometimes", {"Data Analyst": 1}),
        ("Not really", {}),
    ]),
    ("Do you enjoy working independently on long, detail-heavy tasks?", "WorkPreference", [
        ("Yes, I enjoy deep focused work", {"Software Developer": 1, "Data Scientist": 1, "Database Administrator": 1}),
        ("I prefer collaborative, interactive tasks", {"UI/UX Designer": 1, "QA/Software Tester": 1}),
        ("Depends on the task", {}),
    ]),
    ("How comfortable are you with mathematics and statistics?", "Technical", [
        ("Very comfortable", {"Data Scientist": 2, "AI/ML Engineer": 2}),
        ("Somewhat comfortable", {"Data Analyst": 1}),
        ("Not very comfortable", {}),
    ]),
]


def seed(target_app=None):
    if target_app is None:
        from app import create_app
        target_app = create_app()

    with target_app.app_context():
        db.drop_all()
        db.create_all()

        # ---- Skills & Interests ----
        skill_objs = {}
        for s in SKILLS:
            obj = Skill(name=s)
            db.session.add(obj)
            skill_objs[s] = obj

        interest_objs = {}
        for i in INTERESTS:
            obj = Interest(name=i)
            db.session.add(obj)
            interest_objs[i] = obj

        db.session.flush()

        # ---- Careers ----
        career_objs = {}
        for c in CAREERS:
            career = Career(name=c["name"], description=c["description"])
            db.session.add(career)
            db.session.flush()
            career_objs[c["name"]] = career

            for skill_name, level in c["skills"].items():
                db.session.add(CareerSkill(
                    career_id=career.id, skill_id=skill_objs[skill_name].id, required_level=level
                ))

            for interest_name in c["interests"]:
                db.session.add(CareerInterest(
                    career_id=career.id, interest_id=interest_objs[interest_name].id
                ))

            for step_num, (title, bullets) in enumerate(c["roadmap"], start=1):
                db.session.add(RoadmapStep(
                    career_id=career.id, step_number=step_num, title=title,
                    details="\n".join(bullets)
                ))

            for level, titles in c["projects"].items():
                for title in titles:
                    db.session.add(Project(career_id=career.id, level=level, title=title))

        db.session.flush()

        # ---- Quiz Questions ----
        for text, category, options in QUESTIONS:
            question = Question(text=text, category=category)
            db.session.add(question)
            db.session.flush()
            for opt_text, career_points in options:
                option = Option(question_id=question.id, text=opt_text)
                db.session.add(option)
                db.session.flush()
                for career_name, points in career_points.items():
                    db.session.add(OptionCareerScore(
                        option_id=option.id, career_id=career_objs[career_name].id, points=points
                    ))

        # ---- Users: 1 admin + 1 demo student ----
        admin = User(name="Nanda", email="admin@career.local", is_admin=True)
        admin.set_password("Nanda")
        db.session.add(admin)
        db.session.flush()
        db.session.add(Profile(user_id=admin.id))

        student = User(name="Demo Student", email="student@career.local", is_admin=False)
        student.set_password("student123")
        db.session.add(student)
        db.session.flush()
        db.session.add(Profile(
            user_id=student.id, education="BSc Computer Science",
            college="Demo College", year="Final Year", cgpa=7.8,
        ))

        db.session.commit()

        print("Database seeded successfully.")
        print("Admin login   -> admin@career.local (or Nanda) / Nanda")
        print("Student login -> student@career.local / student123")


if __name__ == "__main__":
    seed()

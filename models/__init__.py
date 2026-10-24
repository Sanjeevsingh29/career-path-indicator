"""
models package
---------------
Re-exports the shared `db` instance and every model class so other
modules can simply do:  from models import db, User, Career, ...
"""

from models.db import db
from models.models import (
    User,
    Profile,
    Skill,
    UserSkill,
    Interest,
    UserInterest,
    Career,
    CareerSkill,
    CareerInterest,
    RoadmapStep,
    Project,
    Question,
    Option,
    OptionCareerScore,
    QuizResponse,
    Result,
    LEVEL_SCALE,
)

"""
services/validators.py
-----------------------
Small, dependency-free validation helpers used by the auth routes.
Kept separate from routes/ so the same checks can be unit tested easily.
"""

import re

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_valid_email(email):
    return bool(email) and bool(EMAIL_REGEX.match(email))


def is_valid_password(password):
    """Simple rule: at least 6 characters. Kept intentionally basic -
    this is a student project, not a banking system."""
    return bool(password) and len(password) >= 6


def validate_registration(name, email, password, confirm_password):
    """Returns a list of error strings (empty list = valid)."""
    errors = []
    if not name or not name.strip():
        errors.append("Name is required.")
    if not is_valid_email(email):
        errors.append("Please enter a valid email address.")
    if not is_valid_password(password):
        errors.append("Password must be at least 6 characters long.")
    if password != confirm_password:
        errors.append("Password and Confirm Password do not match.")
    return errors

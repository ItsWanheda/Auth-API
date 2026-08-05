"""Custom validators for usernames and passwords."""

from __future__ import annotations

import re

from app.core.exceptions import ValidationError

_USERNAME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]{2,31}$")


def validate_username(username: str) -> str:
    """Validate a username (3–32 chars, must start with a letter)."""
    if not _USERNAME_RE.match(username):
        raise ValidationError(
            message="Invalid username",
            details={"field": "username", "rules": [
                "3–32 characters", "must start with a letter",
                "letters, digits, '_' and '-' only",
            ]},
        )
    return username


def validate_password_strength(password: str) -> str:
    """Validate password meets strength policy.

    Rules:
        * ≥ 12 and ≤ 128 characters
        * ≥ 1 uppercase, lowercase, digit, and special character
    """
    if len(password) < 12:
        raise ValidationError(message="Password too weak",
                              details={"field": "password", "rules": ["min 12 characters"]})
    if len(password) > 128:
        raise ValidationError(message="Password too long",
                              details={"field": "password", "rules": ["max 128 characters"]})

    rules = [
        (re.compile(r"[A-Z]"), "must contain an uppercase letter"),
        (re.compile(r"[a-z]"), "must contain a lowercase letter"),
        (re.compile(r"\d"), "must contain a digit"),
        (re.compile(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?`~]"),
         "must contain a special character"),
    ]
    failed = [msg for pat, msg in rules if not pat.search(password)]
    if failed:
        raise ValidationError(message="Password too weak",
                              details={"field": "password", "rules": failed})
    return password
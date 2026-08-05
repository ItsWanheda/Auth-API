"""Argon2id password hashing with safe defaults."""

from __future__ import annotations

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

# Tuned for interactive login on modern hardware.
# t=3, m=64MiB, p=4 ≈ 100ms per hash on a 4-core server.
_hasher = PasswordHasher(
    time_cost=3, memory_cost=65536, parallelism=4,
    hash_len=32, salt_len=16, type=2,
)


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except (VerifyMismatchError, InvalidHashError):
        return False


def needs_rehash(password_hash: str) -> bool:
    try:
        return _hasher.check_needs_rehash(password_hash)
    except InvalidHashError:
        return True


def verify_and_upgrade_password(password: str, password_hash: str) -> tuple[bool, str | None]:
    """Verify a password; return (is_valid, upgraded_hash_or_None)."""
    if not verify_password(password, password_hash):
        return False, None
    if needs_rehash(password_hash):
        return True, hash_password(password)
    return True, None
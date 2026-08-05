"""Validator unit tests."""

import pytest
from app.core.exceptions import ValidationError
from app.utils.validators import validate_password_strength, validate_username


class TestUsernameValidation:
    @pytest.mark.parametrize("u", ["john", "j_doe", "John-Doe", "abc123", "user_name_2"])
    def test_valid_usernames(self, u):
        assert validate_username(u) == u

    @pytest.mark.parametrize("u", ["ab", "1john", "jo", "jo!hn", "a" * 33])
    def test_invalid_usernames(self, u):
        with pytest.raises(ValidationError):
            validate_username(u)


class TestPasswordValidation:
    def test_strong_password_passes(self):
        assert validate_password_strength("Sup3r$trongPass!") == "Sup3r$trongPass!"

    @pytest.mark.parametrize("p", ["short1!", "alllowercase1!", "ALLUPPERCASE1!", "NoDigits!!", "Nosp1alchars"])
    def test_weak_passwords_fail(self, p):
        with pytest.raises(ValidationError):
            validate_password_strength(p)
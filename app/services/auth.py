"""Authentication business logic (login, password reset, email verification)."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.core.exceptions import AuthenticationError, NotFoundError
from app.core.logging import get_logger
from app.models.password_reset_token import PasswordResetToken
from app.models.user import User
from app.repositories.token import (
    EmailVerificationTokenRepository, PasswordResetTokenRepository,
)
from app.repositories.user import UserRepository
from app.security.password import hash_password
from app.security.tokens import (
    create_email_verification_token, create_password_reset_token, hash_token,
)
from app.services.token import TokenService

logger = get_logger(__name__)


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)
        self.token_service = TokenService(session)
        self.password_reset_repo = PasswordResetTokenRepository(session)
        self.email_verification_repo = EmailVerificationTokenRepository(session)

    async def authenticate(self, *, identifier: str, password: str,
                           user_agent: str | None = None,
                           ip_address: str | None = None) -> tuple[User, "TokenResponse"]:  # noqa
        from app.schemas.auth import TokenResponse  # local import to avoid cycle
        user = await self.user_repo.get_by_identifier(identifier)
        # Generic error message — never reveal which field is wrong.
        invalid = AuthenticationError("Invalid credentials")

        if not user or not user.is_active:
            logger.info("Login failed: unknown/inactive user", identifier=identifier)
            raise invalid

        # Constant-time-ish check, then re-verify even if missing.
        from app.security.password import verify_password
        if not verify_password(password, user.hashed_password):
            logger.info("Login failed: bad password", user_id=str(user.id))
            raise invalid

        user.last_login_at = datetime.now(timezone.utc)
        self.session.add(user)
        await self.session.flush()

        tokens = await self.token_service.issue_token_pair(
            user, user_agent=user_agent, ip_address=ip_address,
        )
        logger.info("User logged in", user_id=str(user.id))
        return user, tokens

    # ------------------------------------------------------------------
    # Password recovery
    # ------------------------------------------------------------------

    async def request_password_reset(self, email: str) -> tuple[str, str, datetime] | None:
        """Return (raw_token, email, expires_at) or None if user doesn't exist.

        Always returns 200 to the client; email service decides whether to send.
        """
        user = await self.user_repo.get_by_email(email)
        if not user or not user.is_active:
            logger.info("Password reset requested for unknown email", email=email)
            return None

        raw, digest, expires_at = create_password_reset_token(user.id)
        await self.password_reset_repo.create({
            "user_id": user.id,
            "token_hash": digest,
            "expires_at": expires_at,
            "used": False,
        })
        # Invalidate any outstanding reset tokens for this user.
        await self.password_reset_repo.invalidate_all_for_user(user.id)
        await self.password_reset_repo.create({
            "user_id": user.id,
            "token_hash": digest,
            "expires_at": expires_at,
            "used": False,
        })
        logger.info("Password reset token issued", user_id=str(user.id))
        return raw, user.email, expires_at

    async def reset_password(self, *, token: str, new_password: str) -> None:
        digest = hash_token(token)
        record = await self.password_reset_repo.get_valid_by_hash(digest)
        if not record:
            raise NotFoundError("Invalid or expired reset token")

        user = await self.user_repo.get_by_id(record.user_id)
        if not user or not user.is_active:
            raise NotFoundError("User not found")

        user.hashed_password = hash_password(new_password)
        self.session.add(user)
        await self.password_reset_repo.mark_used(record.id)
        # Force re-login on all devices.
        await self.token_service.revoke_all_for_user(user.id)
        logger.info("Password reset successful", user_id=str(user.id))

    # ------------------------------------------------------------------
    # Email verification
    # ------------------------------------------------------------------

    async def issue_email_verification(self, user: User) -> tuple[str, datetime]:
        raw, digest, expires_at = create_email_verification_token(user.id)
        await self.email_verification_repo.invalidate_all_for_user(user.id)
        await self.email_verification_repo.create({
            "user_id": user.id,
            "token_hash": digest,
            "expires_at": expires_at,
            "used": False,
        })
        logger.info("Email verification token issued", user_id=str(user.id))
        return raw, expires_at

    async def verify_email(self, *, token: str) -> User:
        digest = hash_token(token)
        record = await self.email_verification_repo.get_valid_by_hash(digest)
        if not record:
            raise NotFoundError("Invalid or expired verification token")

        user = await self.user_repo.get_by_id(record.user_id)
        if not user:
            raise NotFoundError("User not found")

        user.is_verified = True
        self.session.add(user)
        await self.email_verification_repo.mark_used(record.id)
        logger.info("Email verified", user_id=str(user.id))
        return user

    async def resend_email_verification(self, email: str) -> tuple[str, str, datetime] | None:
        user = await self.user_repo.get_by_email(email)
        if not user or user.is_verified:
            return None
        raw, expires_at = await self.issue_email_verification(user)
        return raw, user.email, expires_at
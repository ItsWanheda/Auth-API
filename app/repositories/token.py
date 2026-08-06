"""Token repositories (refresh / password reset / email verification)."""

from __future__ import annotations

import uuid
from typing import Sequence

from sqlalchemy import select, update

from app.models.base import utc_now
from app.models.email_verification_token import EmailVerificationToken
from app.models.password_reset_token import PasswordResetToken
from app.models.refresh_token import RefreshToken
from app.repositories.base import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    model = RefreshToken

    async def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        return (await self.session.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )).scalar_one_or_none()

    async def revoke(self, token_hash: str) -> bool:
        result = await self.session.execute(
            update(RefreshToken)
            .where(RefreshToken.token_hash == token_hash,
                   RefreshToken.revoked.is_(False))
            .values(revoked=True, revoked_at=utc_now())
        )
        return result.rowcount > 0

    async def revoke_all_for_user(self, user_id: uuid.UUID) -> int:
        result = await self.session.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id,
                   RefreshToken.revoked.is_(False))
            .values(revoked=True, revoked_at=utc_now())
        )
        return result.rowcount

    async def list_active_for_user(self, user_id: uuid.UUID) -> Sequence[RefreshToken]:
        return (await self.session.execute(
            select(RefreshToken)
            .where(RefreshToken.user_id == user_id,
                   RefreshToken.revoked.is_(False))
            .order_by(RefreshToken.created_at.desc())
        )).scalars().all()

    async def cleanup_expired(self) -> int:
        """Bulk-delete all expired refresh tokens (use in scheduled jobs)."""
        from sqlalchemy import delete
        result = await self.session.execute(
            delete(RefreshToken).where(RefreshToken.expires_at < utc_now())
        )
        return result.rowcount


class PasswordResetTokenRepository(BaseRepository[PasswordResetToken]):
    model = PasswordResetToken

    async def get_valid_by_hash(self, token_hash: str) -> PasswordResetToken | None:
        return (await self.session.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.token_hash == token_hash,
                PasswordResetToken.used.is_(False),
                PasswordResetToken.expires_at > utc_now(),
            )
        )).scalar_one_or_none()

    async def mark_used(self, token_id: uuid.UUID) -> None:
        await self.session.execute(
            update(PasswordResetToken)
            .where(PasswordResetToken.id == token_id)
            .values(used=True, used_at=utc_now())
        )

    async def invalidate_all_for_user(self, user_id: uuid.UUID) -> None:
        await self.session.execute(
            update(PasswordResetToken)
            .where(PasswordResetToken.user_id == user_id,
                   PasswordResetToken.used.is_(False))
            .values(used=True, used_at=utc_now())
        )


class EmailVerificationTokenRepository(BaseRepository[EmailVerificationToken]):
    model = EmailVerificationToken

    async def get_valid_by_hash(self, token_hash: str) -> EmailVerificationToken | None:
        return (await self.session.execute(
            select(EmailVerificationToken).where(
                EmailVerificationToken.token_hash == token_hash,
                EmailVerificationToken.used.is_(False),
                EmailVerificationToken.expires_at > utc_now(),
            )
        )).scalar_one_or_none()

    async def mark_used(self, token_id: uuid.UUID) -> None:
        await self.session.execute(
            update(EmailVerificationToken)
            .where(EmailVerificationToken.id == token_id)
            .values(used=True, used_at=utc_now())
        )

    async def invalidate_all_for_user(self, user_id: uuid.UUID) -> None:
        await self.session.execute(
            update(EmailVerificationToken)
            .where(EmailVerificationToken.user_id == user_id,
                   EmailVerificationToken.used.is_(False))
            .values(used=True, used_at=utc_now())
        )
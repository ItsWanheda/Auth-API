"""Token-related business logic (refresh-token rotation, issuance)."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.core.exceptions import TokenError
from app.core.logging import get_logger
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.repositories.token import RefreshTokenRepository
from app.security.jwt import (
    TokenType, create_access_token, create_refresh_token, verify_token,
)
from app.security.tokens import hash_refresh_token
from app.schemas.auth import TokenResponse

logger = get_logger(__name__)


class TokenService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = RefreshTokenRepository(session)

    async def issue_token_pair(
        self, user: User, *, user_agent: str | None = None, ip_address: str | None = None,
    ) -> TokenResponse:
        """Mint a fresh access/refresh pair and persist the hashed refresh token."""
        access, access_exp = create_access_token(
            user_id=user.id,
            additional_claims={"username": user.username, "email": user.email,
                               "is_superuser": user.is_superuser},
        )
        refresh, refresh_exp, refresh_hash = await self._mint_and_store_refresh(
            user=user, user_agent=user_agent, ip_address=ip_address,
        )

        return TokenResponse(
            access_token=access, refresh_token=refresh, token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            refresh_expires_in=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
            access_token_expires_at=access_exp,
            refresh_token_expires_at=refresh_exp,
        )

    async def _mint_and_store_refresh(
        self, user: User, *, user_agent: str | None, ip_address: str | None,
    ) -> tuple[str, datetime, str]:
        # 1. Generate the raw token + its hash.
        raw, _exp = create_refresh_token(user_id=user.id)
        digest = hash_refresh_token(raw)

        # 2. Persist the hash.
        token_row = await self.repo.create({
            "user_id": user.id,
            "token_hash": digest,
            "expires_at": _exp,
            "user_agent": (user_agent or "")[:500],
            "ip_address": (ip_address or "")[:45],
            "revoked": False,
        })
        return raw, token_row.expires_at, digest

    async def rotate(self, refresh_token: str) -> tuple[TokenResponse, User]:
        """Rotate a refresh token: verify JWT, check DB, revoke old, issue new."""
        payload = verify_token(refresh_token, expected_type="refresh")
        user_id = uuid.UUID(payload["sub"])

        digest = hash_refresh_token(refresh_token)
        stored = await self.repo.get_by_hash(digest)
        if not stored:
            # Possible replay of an already-rotated token — fail closed.
            await self.repo.revoke_all_for_user(user_id)
            logger.warning("Refresh-token replay detected; revoked all tokens",
                           user_id=str(user_id))
            raise TokenError("Token not recognized",
                             details={"reason": "unknown_token"})

        if stored.revoked:
            # Reuse of a revoked token — revoke everything for the user.
            await self.repo.revoke_all_for_user(user_id)
            logger.warning("Revoked refresh token reuse detected",
                           user_id=str(user_id))
            raise TokenError("Token has been revoked",
                             details={"reason": "revoked"})

        if stored.is_expired:
            raise TokenError("Refresh token expired", details={"reason": "expired"})

        # Load user (need email for response metadata).
        from app.repositories.user import UserRepository
        user_repo = UserRepository(self.session)
        user = await user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise TokenError("User not found or inactive")

        # Revoke old, issue new.
        await self.repo.revoke(digest)
        token_response = await self.issue_token_pair(user)
        logger.info("Refresh token rotated", user_id=str(user_id))
        return token_response, user

    async def revoke(self, refresh_token: str) -> bool:
        digest = hash_refresh_token(refresh_token)
        revoked = await self.repo.revoke(digest)
        if revoked:
            logger.info("Refresh token revoked", token_hash=digest[:12])
        return revoked

    async def revoke_all_for_user(self, user_id: uuid.UUID) -> int:
        count = await self.repo.revoke_all_for_user(user_id)
        logger.info("All refresh tokens revoked", user_id=str(user_id), count=count)
        return count
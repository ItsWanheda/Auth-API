"""JWT encode/decode for access and refresh tokens."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Literal

import jwt
from jwt.exceptions import DecodeError, ExpiredSignatureError, InvalidTokenError

from app.config.settings import settings
from app.core.exceptions import TokenError

TokenType = Literal["access", "refresh"]


def _create_token(*, subject: str, token_type: TokenType,
                  expires_delta: timedelta,
                  additional_claims: dict[str, Any] | None = None,
                  jti: str | None = None) -> tuple[str, datetime]:
    now = datetime.now(timezone.utc)
    expire = now + expires_delta
    payload: dict[str, Any] = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "type": token_type,
        "jti": jti or str(uuid.uuid4()),
    }
    if additional_claims:
        payload.update(additional_claims)
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, expire


def create_access_token(*, user_id: uuid.UUID,
                        additional_claims: dict[str, Any] | None = None) -> tuple[str, datetime]:
    return _create_token(
        subject=str(user_id), token_type="access",
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        additional_claims=additional_claims,
    )


def create_refresh_token(*, user_id: uuid.UUID, jti: str | None = None) -> tuple[str, datetime]:
    return _create_token(
        subject=str(user_id), token_type="refresh",
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        jti=jti,
    )


def decode_token(token: str, *, expected_type: TokenType | None = None) -> dict[str, Any]:
    try:
        return jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM],
            options={"require": ["exp", "iat", "sub", "type"]},
        )
    except ExpiredSignatureError as exc:
        raise TokenError("Token has expired", details={"reason": "expired"}) from exc
    except DecodeError as exc:
        raise TokenError("Invalid token", details={"reason": "malformed"}) from exc
    except InvalidTokenError as exc:
        raise TokenError("Invalid token", details={"reason": str(exc)}) from exc


def verify_token(token: str, *, expected_type: TokenType) -> dict[str, Any]:
    payload = decode_token(token, expected_type=expected_type)
    if expected_type and payload.get("type") != expected_type:
        raise TokenError(f"Expected {expected_type} token",
                         details={"token_type": payload.get("type")})
    return payload
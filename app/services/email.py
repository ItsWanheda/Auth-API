"""Email service (interface + a console-sending dev implementation).

In production, plug in an SMTP/SES/SendGrid driver here. For local dev and
tests, we just log the email payload.
"""

from __future__ import annotations

from datetime import datetime
from typing import Protocol

from app.config.settings import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmailProvider(Protocol):
    async def send(self, *, to: str, subject: str, html: str, text: str) -> None: ...


class ConsoleEmailProvider:
    """Dev/test provider that logs the email body."""

    async def send(self, *, to: str, subject: str, html: str, text: str) -> None:
        logger.info("📧 Email sent (console)",
                    to=to, subject=subject, text=text[:200],
                    html_len=len(html), timestamp=datetime.utcnow().isoformat())


class EmailService:
    def __init__(self, provider: EmailProvider | None = None) -> None:
        self.provider = provider or ConsoleEmailProvider()

    async def send_verification(self, *, to_email: str, token: str) -> None:
        link = f"{settings.FRONTEND_URL}/verify-email?token={token}"
        await self.provider.send(
            to=to_email, subject=f"{settings.APP_NAME}: verify your email",
            text=f"Click to verify your account: {link}",
            html=f"<p>Click <a href='{link}'>here</a> to verify your account.</p>",
        )

    async def send_password_reset(self, *, to_email: str, token: str) -> None:
        link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        await self.provider.send(
            to=to_email, subject=f"{settings.APP_NAME}: reset your password",
            text=f"Reset your password using this link (valid for "
                 f"{settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS}h): {link}",
            html=f"<p>Click <a href='{link}'>here</a> to reset your password.</p>",
        )
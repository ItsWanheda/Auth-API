"""Authentication endpoints (register, login, refresh, logout, password, email)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Request, Response, status

from app.config.settings import settings
from app.dependencies.auth import get_current_user
from app.dependencies.services import (
    get_auth_service, get_email_service, get_token_service,
)
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest, LoginRequest, LogoutAllResponse, LogoutResponse,
    MessageResponse, PasswordChangeRequest, RefreshTokenRequest,
    RegisterRequest, ResendVerificationRequest, ResetPasswordRequest,
    TokenResponse, VerifyEmailRequest,
)
from app.schemas.common import SuccessResponse
from app.schemas.user import UserPublic
from app.services.auth import AuthService
from app.services.email import EmailService
from app.services.token import TokenService

router = APIRouter(prefix="/auth", tags=["authentication"])


# ----------------------------------------------------------------------
# Registration
# ----------------------------------------------------------------------


@router.post(
    "/register",
    response_model=SuccessResponse[UserPublic],
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(
    payload: RegisterRequest,
    background_tasks: BackgroundTasks,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    email_service: Annotated[EmailService, Depends(get_email_service)],
) -> SuccessResponse[UserPublic]:
    user = await auth_service.user_repo.create_user_from_payload(payload) if False else None  # noqa
    # We delegate to AuthService.register-like flow via UserService.
    from app.dependencies.services import get_user_service
    from app.services.user import UserService
    user_service = get_user_service(auth_service.session)

    user = await user_service.register(
        username=payload.username, email=payload.email,
        password=payload.password, full_name=payload.full_name,
    )

    # Issue verification token & send email in the background.
    raw_token, _expires = await auth_service.issue_email_verification(user)
    background_tasks.add_task(email_service.send_verification,
                              to_email=user.email, token=raw_token)

    return SuccessResponse(data=UserPublic.model_validate(user))


# ----------------------------------------------------------------------
# Login
# ----------------------------------------------------------------------


@router.post(
    "/login",
    response_model=SuccessResponse[TokenResponse],
    summary="Login with email or username",
)
async def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> SuccessResponse[TokenResponse]:
    user, tokens = await auth_service.authenticate(
        identifier=payload.identifier, password=payload.password,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )
    _set_refresh_cookie(response, tokens.refresh_token)
    return SuccessResponse(data=tokens, meta={"user": {"id": str(user.id)}})


# ----------------------------------------------------------------------
# Refresh
# ----------------------------------------------------------------------


@router.post(
    "/refresh",
    response_model=SuccessResponse[TokenResponse],
    summary="Rotate refresh token",
)
async def refresh_token(
    payload: RefreshTokenRequest,
    request: Request,
    response: Response,
    token_service: Annotated[TokenService, Depends(get_token_service)],
) -> SuccessResponse[TokenResponse]:
    tokens, _user = await token_service.rotate(
        refresh_token=payload.refresh_token,
    )
    _set_refresh_cookie(response, tokens.refresh_token)
    return SuccessResponse(data=tokens)


# ----------------------------------------------------------------------
# Logout
# ----------------------------------------------------------------------


@router.post(
    "/logout",
    response_model=SuccessResponse[LogoutResponse],
    summary="Logout current device (revoke refresh token)",
)
async def logout(
    payload: RefreshTokenRequest,
    response: Response,
    token_service: Annotated[TokenService, Depends(get_token_service)],
) -> SuccessResponse[LogoutResponse]:
    await token_service.revoke(payload.refresh_token)
    _clear_refresh_cookie(response)
    return SuccessResponse(data=LogoutResponse(message="Logged out successfully"))


@router.post(
    "/logout-all",
    response_model=SuccessResponse[LogoutAllResponse],
    summary="Logout all devices",
)
async def logout_all(
    response: Response,
    current_user: Annotated[User, Depends(get_current_user)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
) -> SuccessResponse[LogoutAllResponse]:
    count = await token_service.revoke_all_for_user(current_user.id)
    _clear_refresh_cookie(response)
    return SuccessResponse(data=LogoutAllResponse(
        message=f"Logged out from {count} session(s)", revoked_count=count))


# ----------------------------------------------------------------------
# Password
# ----------------------------------------------------------------------


@router.post(
    "/forgot-password",
    response_model=SuccessResponse[MessageResponse],
    summary="Request a password reset email",
)
async def forgot_password(
    payload: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    email_service: Annotated[EmailService, Depends(get_email_service)],
) -> SuccessResponse[MessageResponse]:
    result = await auth_service.request_password_reset(payload.email)
    if result:
        raw_token, email, _expires = result
        background_tasks.add_task(email_service.send_password_reset,
                                  to_email=email, token=raw_token)
    # Always return same response — do not leak whether the email exists.
    return SuccessResponse(
        data=MessageResponse(message="If the email exists, a reset link has been sent"))


@router.post(
    "/reset-password",
    response_model=SuccessResponse[MessageResponse],
    summary="Reset password using a valid reset token",
)
async def reset_password(
    payload: ResetPasswordRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> SuccessResponse[MessageResponse]:
    await auth_service.reset_password(
        token=payload.token, new_password=payload.password,
    )
    return SuccessResponse(
        data=MessageResponse(message="Password reset successful — please log in"))


@router.post(
    "/change-password",
    response_model=SuccessResponse[MessageResponse],
    summary="Change password (authenticated)",
)
async def change_password(
    payload: PasswordChangeRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
):
    from app.services.user import UserService
    user_service = UserService(token_service.session)
    await user_service.change_password(
        current_user, current=payload.current_password, new=payload.new_password,
    )
    # Revoke all sessions so other devices must re-authenticate.
    revoked = await token_service.revoke_all_for_user(current_user.id)
    return SuccessResponse(
        data=MessageResponse(message=f"Password changed. {revoked} session(s) revoked."))


# ----------------------------------------------------------------------
# Email verification
# ----------------------------------------------------------------------


@router.post(
    "/verify-email",
    response_model=SuccessResponse[MessageResponse],
    summary="Verify email with token",
)
async def verify_email(
    payload: VerifyEmailRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> SuccessResponse[MessageResponse]:
    await auth_service.verify_email(token=payload.token)
    return SuccessResponse(data=MessageResponse(message="Email verified successfully"))


@router.post(
    "/resend-verification",
    response_model=SuccessResponse[MessageResponse],
    summary="Resend the email verification link",
)
async def resend_verification(
    payload: ResendVerificationRequest,
    background_tasks: BackgroundTasks,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    email_service: Annotated[EmailService, Depends(get_email_service)],
) -> SuccessResponse[MessageResponse]:
    result = await auth_service.resend_email_verification(payload.email)
    if result:
        raw_token, email, _ = result
        background_tasks.add_task(email_service.send_verification,
                                  to_email=email, token=raw_token)
    return SuccessResponse(
        data=MessageResponse(message="If the account exists and is unverified, an email has been sent"))


# ----------------------------------------------------------------------
# Cookie helpers
# ----------------------------------------------------------------------


def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=settings.REFRESH_TOKEN_COOKIE_NAME, value=token,
        httponly=settings.COOKIE_HTTPONLY, secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE, max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        path="/api/v1/auth",  # cookie only sent to auth endpoints
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(settings.REFRESH_TOKEN_COOKIE_NAME, path="/api/v1/auth")
"""User profile endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_active_user, get_current_user
from app.dependencies.services import get_token_service, get_user_service
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.user import UserPublic, UserUpdate
from app.services.token import TokenService
from app.services.user import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=SuccessResponse[UserPublic], summary="Get current profile")
async def get_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> SuccessResponse[UserPublic]:
    return SuccessResponse(data=UserPublic.model_validate(current_user))


@router.patch("/me", response_model=SuccessResponse[UserPublic], summary="Update current profile")
async def update_me(
    payload: UserUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> SuccessResponse[UserPublic]:
    updated = await user_service.update_profile(current_user, payload)
    return SuccessResponse(data=UserPublic.model_validate(updated))


@router.delete("/me", response_model=SuccessResponse[dict], summary="Soft-delete account")
async def delete_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
) -> SuccessResponse[dict]:
    current_user.is_active = False
    user_service.session.add(current_user)
    await token_service.revoke_all_for_user(current_user.id)
    return SuccessResponse(data={"deactivated": True})
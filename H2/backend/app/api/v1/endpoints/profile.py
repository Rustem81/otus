from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user, require_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.profile import (
    BanksListResponse,
    ErrorResponse,
    OnboardingRequest,
    SavedFiltersResponse,
    SavedFiltersUpdate,
    TraderProfileResponse,
    TraderProfileUpdate,
)
from app.services.profile_service import ProfileService

router = APIRouter()


async def get_profile_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ProfileService:
    """Factory dependency for ProfileService."""
    return ProfileService(db)


@router.get(
    "/",
    response_model=TraderProfileResponse,
    dependencies=[require_user],
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
)
async def get_profile(
    current_user: Annotated[User, Depends(get_current_active_user)],
    profile_service: Annotated[ProfileService, Depends(get_profile_service)],
) -> TraderProfileResponse:
    """
    Get current user's trader profile.

    Creates default profile if none exists.
    """
    profile = await profile_service.get_profile(current_user.id)
    return ProfileService.profile_to_response(profile)


@router.put(
    "/",
    response_model=TraderProfileResponse,
    dependencies=[require_user],
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        422: {"model": ErrorResponse, "description": "Validation error"},
    },
)
async def update_profile(
    update_data: TraderProfileUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    profile_service: Annotated[ProfileService, Depends(get_profile_service)],
) -> TraderProfileResponse:
    """
    Update current user's trader profile.

    Only provided fields are updated.
    """
    profile = await profile_service.update_profile(current_user.id, update_data)
    return ProfileService.profile_to_response(profile)


@router.get(
    "/banks",
    response_model=BanksListResponse,
    dependencies=[require_user],
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
)
async def get_banks(
    profile_service: Annotated[ProfileService, Depends(get_profile_service)],
) -> BanksListResponse:
    """
    Get list of available banks and payment methods.
    """
    banks = await profile_service.get_available_banks()
    return BanksListResponse(banks=banks)


@router.get(
    "/filters",
    response_model=SavedFiltersResponse,
    dependencies=[require_user],
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
)
async def get_saved_filters(
    current_user: Annotated[User, Depends(get_current_active_user)],
    profile_service: Annotated[ProfileService, Depends(get_profile_service)],
) -> SavedFiltersResponse:
    """
    Get current user's saved advertisement filters.
    """
    filters = await profile_service.get_saved_filters(current_user.id)
    return ProfileService.filters_to_response(filters)


@router.put(
    "/filters",
    response_model=SavedFiltersResponse,
    dependencies=[require_user],
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        422: {"model": ErrorResponse, "description": "Validation error"},
    },
)
async def update_saved_filters(
    filters_data: SavedFiltersUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    profile_service: Annotated[ProfileService, Depends(get_profile_service)],
) -> SavedFiltersResponse:
    """
    Save advertisement filters for current user.

    Replaces existing filters.
    """
    filters = await profile_service.update_saved_filters(current_user.id, filters_data)
    return ProfileService.filters_to_response(filters)


@router.post(
    "/onboarding",
    response_model=TraderProfileResponse,
    dependencies=[require_user],
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
)
async def complete_onboarding(
    data: OnboardingRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    profile_service: Annotated[ProfileService, Depends(get_profile_service)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TraderProfileResponse:
    """
    Complete onboarding wizard.

    Sets up trader profile and marks onboarding as completed.
    """
    # Update profile with onboarding data
    update_data = TraderProfileUpdate(
        payment_methods=data.payment_methods,
        min_amount=data.min_amount,
        max_amount=data.max_amount,
        risk_profile=data.risk_profile,
        commission_percent=data.commission_percent,
        commission_fixed=data.commission_fixed,
    )
    profile = await profile_service.update_profile(current_user.id, update_data)

    # Mark onboarding as completed
    current_user.onboarding_completed = True
    await db.commit()

    return ProfileService.profile_to_response(profile)

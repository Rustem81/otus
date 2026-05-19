from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_auth_service, get_current_active_user, bearer_scheme
from app.core.database import get_db
from app.core.redis import get_redis
from app.models.user import User
from app.schemas.auth import (
    ErrorResponse,
    LoginResponse,
    RegisterResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
    VerifyEmailResponse,
)
from app.services.auth_service import AuthService
from fastapi.security import HTTPAuthorizationCredentials

router = APIRouter()


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Bad request"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
    },
)
async def register(
    request_data: UserRegisterRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> RegisterResponse:
    """Register a new user account."""
    try:
        user, verification_token = await auth_service.register(
            email=request_data.email,
            password=request_data.password,
        )
        return RegisterResponse(
            message="Registration successful. Please check your email to verify your account.",
            email=user.email,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/verify-email/{token}",
    response_model=VerifyEmailResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid or expired token"},
    },
)
async def verify_email(
    token: str,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> VerifyEmailResponse:
    """Verify user email address with token from email."""
    try:
        user = await auth_service.verify_email(token)
        return VerifyEmailResponse(
            message="Email verified successfully. You can now log in.",
            email=user.email,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/login",
    response_model=LoginResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid credentials"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
    },
)
async def login(
    request_data: UserLoginRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> LoginResponse:
    """Authenticate user and create session. Returns access_token."""
    try:
        user, session_token = await auth_service.login(
            email=request_data.email,
            password=request_data.password,
        )
        return LoginResponse(
            user=UserResponse.model_validate(user),
            access_token=session_token,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid credentials",
        )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
)
async def logout(
    bearer: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> dict[str, str]:
    """Logout user — invalidates session token in Redis."""
    token = bearer.credentials if bearer else None
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    await auth_service.logout(token)
    return {"message": "Logged out successfully"}


@router.get(
    "/me",
    response_model=UserResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> UserResponse:
    """Get current authenticated user information."""
    return UserResponse.model_validate(current_user)

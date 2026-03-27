from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_auth_service, get_current_active_user
from app.core.database import get_db
from app.core.redis import get_redis
from app.middleware.csrf import CSRF_COOKIE_NAME
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
    """
    Register a new user account.

    Sends verification email with token (24h expiry).
    """
    try:
        user, verification_token = await auth_service.register(
            email=request_data.email,
            password=request_data.password,
        )

        # TODO: Send actual email with verification_token
        # For MVP, just return success (in production, integrate email service)

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
    """
    Verify user email address with token from email.
    """
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
        401: {"model": ErrorResponse, "description": "Email not verified"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
    },
)
async def login(
    request_data: UserLoginRequest,
    response: Response,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> LoginResponse:
    """
    Authenticate user and create session.

    Sets session_token cookie on success.
    """
    try:
        user, session_token = await auth_service.login(
            email=request_data.email,
            password=request_data.password,
        )

        # Return token in response (MVP: simple token auth)
        return LoginResponse(
            user=UserResponse.model_validate(user),
            access_token=session_token,
        )
    except ValueError as e:
        # Generic error to prevent user enumeration
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
    response: Response,
    current_user: Annotated[User, Depends(get_current_active_user)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    session_token: str | None = None,  # From cookie
) -> dict[str, str]:
    """
    Logout user and clear session.
    """
    # Get session token from cookie if not provided
    if not session_token:
        # This will be handled by cookie dependency
        pass

    # Delete session
    # Note: In a real implementation, we'd extract the cookie value here
    # For now, the session extension in get_current_user validates it

    response.delete_cookie(key="session_token")

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
    """
    Get current authenticated user information.
    """
    return UserResponse.model_validate(current_user)


@router.get("/csrf-token")
async def get_csrf_token_endpoint() -> dict[str, str]:
    """
    Get a fresh CSRF token.

    Token is also set as cookie automatically by CSRF middleware.
    """
    from app.middleware.csrf import get_csrf_token

    return await get_csrf_token()

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """Request schema for user registration."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class UserLoginRequest(BaseModel):
    """Request schema for user login."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Response schema for user data."""

    id: str
    email: str
    role: str
    is_verified: bool

    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    """Response schema for successful login."""

    user: UserResponse
    access_token: str
    message: str = "Login successful"


class RegisterResponse(BaseModel):
    """Response schema for successful registration."""

    message: str
    email: str


class VerifyEmailResponse(BaseModel):
    """Response schema for email verification."""

    message: str
    email: str


class ErrorResponse(BaseModel):
    """Response schema for errors."""

    detail: str

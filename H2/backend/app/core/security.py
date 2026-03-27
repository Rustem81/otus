from __future__ import annotations

import secrets
import uuid
from datetime import datetime, timedelta, timezone

import bcrypt

from app.core.config import get_settings

settings = get_settings()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password using bcrypt."""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def generate_session_token() -> str:
    """Generate a cryptographically secure session token."""
    return secrets.token_urlsafe(32)


def generate_verification_token() -> str:
    """Generate a unique email verification token."""
    return str(uuid.uuid4())


def get_session_expiry() -> datetime:
    """Get session expiration time (24 hours from now)."""
    return datetime.now(timezone.utc) + timedelta(hours=24)


def get_verification_expiry() -> datetime:
    """Get email verification token expiration time (24 hours from now)."""
    return datetime.now(timezone.utc) + timedelta(hours=24)

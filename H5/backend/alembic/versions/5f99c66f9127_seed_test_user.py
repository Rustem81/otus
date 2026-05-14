"""Seed test user

Revision ID: 5f99c66f9127
Revises: 96090f785ff2
Create Date: 2026-03-26 15:37:29.104952

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import bcrypt


# revision identifiers, used by Alembic.
revision: str = '5f99c66f9127'
down_revision: Union[str, None] = '96090f785ff2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def hash_password(password: str) -> str:
    """Hash password using bcrypt directly."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def upgrade() -> None:
    """Seed test user for development."""
    hashed_password = hash_password("test123456")

    users_table = sa.table(
        "users",
        sa.column("id", sa.String),
        sa.column("email", sa.String),
        sa.column("hashed_password", sa.String),
        sa.column("role", sa.String),
        sa.column("is_verified", sa.Boolean),
    )

    op.bulk_insert(
        users_table,
        [
            {
                "id": "test-user-001",
                "email": "test@test.com",
                "hashed_password": hashed_password,
                "role": "USER",
                "is_verified": True,
            },
            {
                "id": "admin-user-001",
                "email": "admin@test.com",
                "hashed_password": hash_password("admin1234"),
                "role": "ADMIN",
                "is_verified": True,
            },
        ],
    )


def downgrade() -> None:
    """Remove seed test users."""
    op.execute(
        sa.text("DELETE FROM users WHERE id IN ('test-user-001', 'admin-user-001')")
    )

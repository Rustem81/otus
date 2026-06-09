"""Add OAuth fields to users table

Revision ID: b7c8d9e0f1a2
Revises: a1b2c3d4e5f6
Create Date: 2025-01-20 10:00:00.000000

"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy import text

from alembic import op

revision: str = "b7c8d9e0f1a2"
down_revision: str | None = "a1b2c3d4e5f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add OAuth provider and subject columns
    op.add_column(
        "users",
        sa.Column("oauth_provider", sa.String(32), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("oauth_subject", sa.String(255), nullable=True),
    )

    # Create unique partial index for OAuth identity
    op.create_index(
        "ix_users_oauth",
        "users",
        ["oauth_provider", "oauth_subject"],
        unique=True,
        postgresql_where=text("oauth_provider IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("ix_users_oauth", table_name="users")
    op.drop_column("users", "oauth_subject")
    op.drop_column("users", "oauth_provider")

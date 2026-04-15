"""Add v1.1 features: onboarding, blacklist, view history, KYC

Revision ID: a1b2c3d4e5f6
Revises: 5f99c66f9127
Create Date: 2026-04-15 12:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "5f99c66f9127"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Onboarding flag on users
    op.add_column(
        "users",
        sa.Column("onboarding_completed", sa.Boolean(), nullable=False, server_default="false"),
    )

    # Mark existing test users as onboarding completed
    op.execute(
        sa.text("UPDATE users SET onboarding_completed = true WHERE id IN ('test-user-001', 'admin-user-001')")
    )

    # Merchant blacklist
    op.create_table(
        "merchant_blacklist",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("merchant_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "merchant_id", name="uq_blacklist_user_merchant"),
    )

    # View history
    op.create_table(
        "view_history",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("advertisement_id", sa.String(length=36), nullable=False),
        sa.Column("viewed_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["advertisement_id"], ["advertisements.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_view_history_user_id", "view_history", ["user_id"])

    # KYC fields on trader_profiles
    op.add_column(
        "trader_profiles",
        sa.Column("kyc_level", sa.String(length=20), nullable=True),
    )
    op.add_column(
        "trader_profiles",
        sa.Column("country", sa.String(length=10), nullable=True, server_default="RU"),
    )
    op.add_column(
        "trader_profiles",
        sa.Column("kyc_limit_warning", sa.Numeric(precision=18, scale=2), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("trader_profiles", "kyc_limit_warning")
    op.drop_column("trader_profiles", "country")
    op.drop_column("trader_profiles", "kyc_level")
    op.drop_index("ix_view_history_user_id", table_name="view_history")
    op.drop_table("view_history")
    op.drop_table("merchant_blacklist")
    op.drop_column("users", "onboarding_completed")

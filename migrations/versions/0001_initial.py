"""Initial migration — create auth_users and users tables

Revision ID: 0001
Revises: 
Create Date: 2026-06-27
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "auth_users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(50), unique=True, nullable=False),
        sa.Column("password_hash", sa.String(100), nullable=False),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("email", sa.String(50), unique=True, nullable=False),
        sa.Column("password_hash", sa.String(100), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("users")
    op.drop_table("auth_users")

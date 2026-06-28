"""add timestamps to auth_users and users

Revision ID: 323451ef83c4
Revises: 0001
Create Date: 2026-06-28 10:14:49.630227

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '323451ef83c4'
down_revision: Union[str, None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("auth_users", sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False))
    op.add_column("auth_users", sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False))
    op.add_column("users", sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False))
    op.add_column("users", sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False))


def downgrade() -> None:
    op.drop_column("auth_users", "created_at")
    op.drop_column("auth_users", "updated_at")
    op.drop_column("users", "created_at")
    op.drop_column("users", "updated_at")

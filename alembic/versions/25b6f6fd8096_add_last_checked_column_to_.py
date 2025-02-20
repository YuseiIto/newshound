"""Add last_checked column to subscriptions table

Revision ID: 25b6f6fd8096
Revises: 85e820330e81
Create Date: 2025-02-19 17:31:30.846968

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "25b6f6fd8096"
down_revision: Union[str, None] = "85e820330e81"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("subscriptions", sa.Column("last_checked", sa.String, nullable=True))


def downgrade() -> None:
    op.drop_column("subscriptions", "last_checked")

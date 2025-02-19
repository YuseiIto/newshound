"""Initial setup

Revision ID: 85e820330e81
Revises: 
Create Date: 2025-02-19 15:43:33.769239

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '85e820330e81'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.create_table(
        'subscriptions',
        sa.Column('channel_id', sa.Integer, primary_key=True),
        sa.Column('feed_url', sa.Text, primary_key=True),
        sa.UniqueConstraint('channel_id', 'feed_url')
    )


def downgrade() -> None:
  op.drop_table('subscriptions')

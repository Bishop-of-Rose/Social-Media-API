"""Adding Token Whitelist

Revision ID: fdc9191565a9
Revises: 1f2b5184d7ac
Create Date: 2026-06-26 13:08:46.417247

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fdc9191565a9'
down_revision: Union[str, Sequence[str], None] = '1f2b5184d7ac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'whitelist',
        sa.Column('jti', sa.String(), index=True, nullable=False),
        sa.Column('expire', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('jti')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("whitelist")

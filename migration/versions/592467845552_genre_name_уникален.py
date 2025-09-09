"""Genre name уникален

Revision ID: 592467845552
Revises: f58a5a7bd9d6
Create Date: 2025-09-09 14:34:52.683659

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '592467845552'
down_revision: Union[str, Sequence[str], None] = 'f58a5a7bd9d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

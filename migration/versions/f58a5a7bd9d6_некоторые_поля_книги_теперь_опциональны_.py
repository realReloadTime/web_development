"""Некоторые поля книги теперь опциональны, например, ISBN

Revision ID: f58a5a7bd9d6
Revises: a6531f0d6407
Create Date: 2025-09-09 01:00:57.920714

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f58a5a7bd9d6'
down_revision: Union[str, Sequence[str], None] = 'a6531f0d6407'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

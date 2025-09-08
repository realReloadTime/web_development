"""Добавлено поле ЗАРЕЗЕРВИРОВАНО для книги - отсылает на id пользователя

Revision ID: a6531f0d6407
Revises: 0090a361b51f
Create Date: 2025-09-09 00:27:12.948807

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a6531f0d6407'
down_revision: Union[str, Sequence[str], None] = '0090a361b51f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

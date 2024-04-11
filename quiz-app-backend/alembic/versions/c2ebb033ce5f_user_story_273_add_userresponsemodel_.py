"""User story 273: Add UserResponseModel and related relationships

Revision ID: c2ebb033ce5f
Revises: 15568dd14de0
Create Date: 2024-04-11 01:26:12.077936

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c2ebb033ce5f'
down_revision: Union[str, None] = '15568dd14de0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

"""User Story 263: Add is_public field to question_sets table

Revision ID: 9a00fb4f32cc
Revises: 9264884a8e59
Create Date: 2024-04-06 05:13:19.479912

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9a00fb4f32cc'
down_revision: Union[str, None] = '9264884a8e59'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('question_sets', sa.Column('is_public', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('question_sets', 'is_public')
    # ### end Alembic commands ###
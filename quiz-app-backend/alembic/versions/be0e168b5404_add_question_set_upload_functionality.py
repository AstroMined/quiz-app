"""Add question set upload functionality

Revision ID: be0e168b5404
Revises: 0cfeaa3d22eb
Create Date: 2024-04-02 22:41:38.942617

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'be0e168b5404'
down_revision: Union[str, None] = '0cfeaa3d22eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('questions', sa.Column('explanation', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('questions', 'explanation')
    # ### end Alembic commands ###

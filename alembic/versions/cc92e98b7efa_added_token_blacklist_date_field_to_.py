"""Added token_blacklist_date field to UserModel

Revision ID: cc92e98b7efa
Revises: beccebd66ce8
Create Date: 2024-09-14 15:13:45.274759

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cc92e98b7efa'
down_revision: Union[str, None] = 'beccebd66ce8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('token_blacklist_date', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'token_blacklist_date')
    # ### end Alembic commands ###

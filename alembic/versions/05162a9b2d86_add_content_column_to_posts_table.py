"""add content column to posts table

Revision ID: 05162a9b2d86
Revises: 9248fb751844
Create Date: 2024-07-12 22:58:39.271103

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '05162a9b2d86'
down_revision: Union[str, None] = '9248fb751844'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))
    pass

def downgrade():
    op.drop_column('posts', 'content')
    pass

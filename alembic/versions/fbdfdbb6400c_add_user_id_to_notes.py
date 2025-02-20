"""add user_id to notes

Revision ID: fbdfdbb6400c
Revises: ef5d3595998c
Create Date: 2025-02-19 22:32:05.276099

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fbdfdbb6400c'
down_revision: Union[str, None] = 'ef5d3595998c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('notes', sa.Column('user_id', sa.String(), nullable=True))
    op.create_index(op.f('ix_notes_user_id'), 'notes', ['user_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_notes_user_id'), table_name='notes')
    op.drop_column('notes', 'user_id')
    # ### end Alembic commands ###

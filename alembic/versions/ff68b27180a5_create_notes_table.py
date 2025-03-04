"""create notes table

Revision ID: ff68b27180a5
Revises: 
Create Date: 2025-02-15 18:40:21.210878

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ff68b27180a5'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('notes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('filename', sa.String(), nullable=True),
    sa.Column('transcription', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notes_filename'), 'notes', ['filename'], unique=False)
    op.create_index(op.f('ix_notes_id'), 'notes', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_notes_id'), table_name='notes')
    op.drop_index(op.f('ix_notes_filename'), table_name='notes')
    op.drop_table('notes')
    # ### end Alembic commands ###

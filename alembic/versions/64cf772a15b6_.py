"""empty message

Revision ID: 64cf772a15b6
Revises: 3fd7f705e42d
Create Date: 2022-05-30 12:05:44.135725

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '64cf772a15b6'
down_revision = '3fd7f705e42d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('callbackxendit',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('event', sa.String(length=256), nullable=True),
    sa.Column('external_id', sa.String(length=256), nullable=True),
    sa.Column('ammount', sa.Float(), nullable=True),
    sa.Column('status', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_callbackxendit_id'), 'callbackxendit', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_callbackxendit_id'), table_name='callbackxendit')
    op.drop_table('callbackxendit')
    # ### end Alembic commands ###
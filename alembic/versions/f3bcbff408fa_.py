"""empty message

Revision ID: f3bcbff408fa
Revises: 5c93c566b1c9
Create Date: 2022-05-23 13:22:13.578313

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f3bcbff408fa'
down_revision = '5c93c566b1c9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('kritiksaran',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('label', sa.String(length=256), nullable=True),
    sa.Column('body', sa.Text(), nullable=True),
    sa.Column('account_id', sa.Integer(), nullable=True),
    sa.Column('createdAt', sa.String(length=128), nullable=True),
    sa.ForeignKeyConstraint(['account_id'], ['account.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_kritiksaran_id'), 'kritiksaran', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_kritiksaran_id'), table_name='kritiksaran')
    op.drop_table('kritiksaran')
    # ### end Alembic commands ###

"""empty message

Revision ID: 0bae35c85597
Revises: 414662f26ba2
Create Date: 2022-05-23 08:39:39.017166

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0bae35c85597'
down_revision = '414662f26ba2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('service_fee',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=True),
    sa.Column('nominal', sa.BigInteger(), nullable=True),
    sa.Column('toko_id', sa.Integer(), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), nullable=True),
    sa.Column('createdAt', sa.String(length=128), nullable=True),
    sa.ForeignKeyConstraint(['toko_id'], ['toko.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_service_fee_id'), 'service_fee', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_service_fee_id'), table_name='service_fee')
    op.drop_table('service_fee')
    # ### end Alembic commands ###

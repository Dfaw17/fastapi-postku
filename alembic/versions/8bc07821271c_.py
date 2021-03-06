"""empty message

Revision ID: 8bc07821271c
Revises: f3bcbff408fa
Create Date: 2022-05-23 14:11:21.581402

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8bc07821271c'
down_revision = 'f3bcbff408fa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('absen',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('photo_absen1', sa.Text(), nullable=True),
    sa.Column('photo_absen1_url', sa.Text(), nullable=True),
    sa.Column('time_abesn1', sa.String(length=128), nullable=True),
    sa.Column('photo_absen2', sa.Text(), nullable=True),
    sa.Column('photo_absen2_url', sa.Text(), nullable=True),
    sa.Column('time_abesn2', sa.String(length=128), nullable=True),
    sa.Column('account_id', sa.Integer(), nullable=True),
    sa.Column('toko_id', sa.Integer(), nullable=True),
    sa.Column('createdAt', sa.String(length=128), nullable=True),
    sa.ForeignKeyConstraint(['account_id'], ['account.id'], ),
    sa.ForeignKeyConstraint(['toko_id'], ['toko.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_absen_id'), 'absen', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_absen_id'), table_name='absen')
    op.drop_table('absen')
    # ### end Alembic commands ###

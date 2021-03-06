"""empty message

Revision ID: 62fb8cb88984
Revises: 8bc07821271c
Create Date: 2022-05-23 14:38:53.806298

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '62fb8cb88984'
down_revision = '8bc07821271c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('absen', sa.Column('time_abesen1', sa.String(length=128), nullable=True))
    op.add_column('absen', sa.Column('time_abesen2', sa.String(length=128), nullable=True))
    op.drop_column('absen', 'time_abesn1')
    op.drop_column('absen', 'time_abesn2')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('absen', sa.Column('time_abesn2', mysql.VARCHAR(length=128), nullable=True))
    op.add_column('absen', sa.Column('time_abesn1', mysql.VARCHAR(length=128), nullable=True))
    op.drop_column('absen', 'time_abesen2')
    op.drop_column('absen', 'time_abesen1')
    # ### end Alembic commands ###

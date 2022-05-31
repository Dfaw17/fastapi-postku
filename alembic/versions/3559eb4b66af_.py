"""empty message

Revision ID: 3559eb4b66af
Revises: 7558a2c6ad14
Create Date: 2022-05-14 21:23:57.994250

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3559eb4b66af'
down_revision = '7558a2c6ad14'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('toko', sa.Column('name', sa.String(length=256), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('toko', 'name')
    # ### end Alembic commands ###
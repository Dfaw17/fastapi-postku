"""empty message

Revision ID: e6a24c94f4d9
Revises: 1440fb7182e3
Create Date: 2022-05-14 12:05:40.220105

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e6a24c94f4d9'
down_revision = '1440fb7182e3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('account', sa.Column('dcd', sa.String(length=640), nullable=True))
    op.add_column('account', sa.Column('key_dcd', sa.String(length=640), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('account', 'key_dcd')
    op.drop_column('account', 'dcd')
    # ### end Alembic commands ###

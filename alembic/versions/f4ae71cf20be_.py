"""empty message

Revision ID: f4ae71cf20be
Revises: 262ca1977aad
Create Date: 2022-05-14 12:28:56.603492

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f4ae71cf20be'
down_revision = '262ca1977aad'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('account', sa.Column('phone', sa.String(length=256), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('account', 'phone')
    # ### end Alembic commands ###
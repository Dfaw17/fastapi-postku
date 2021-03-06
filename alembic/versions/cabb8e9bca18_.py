"""empty message

Revision ID: cabb8e9bca18
Revises: fbfccd497eb7
Create Date: 2022-05-16 19:55:09.327369

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cabb8e9bca18'
down_revision = 'fbfccd497eb7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('menu', sa.Column('kategori_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'menu', 'kategori_menu', ['kategori_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'menu', type_='foreignkey')
    op.drop_column('menu', 'kategori_id')
    # ### end Alembic commands ###

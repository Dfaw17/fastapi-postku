"""empty message

Revision ID: a2cf7f0344cc
Revises: 11d22aa2d8df
Create Date: 2022-05-16 10:28:26.016515

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a2cf7f0344cc'
down_revision = '11d22aa2d8df'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('menu', sa.Column('photo_menu', sa.Text(), nullable=True))
    op.add_column('menu', sa.Column('photo_menu_url', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('menu', 'photo_menu_url')
    op.drop_column('menu', 'photo_menu')
    # ### end Alembic commands ###

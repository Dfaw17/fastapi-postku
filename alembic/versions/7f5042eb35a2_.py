"""empty message

Revision ID: 7f5042eb35a2
Revises: 8d5761233273
Create Date: 2022-05-23 10:11:21.367405

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '7f5042eb35a2'
down_revision = '8d5761233273'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('banner', sa.Column('body', sa.Text(), nullable=True))
    op.drop_column('banner', 'harga_asli')
    op.drop_column('banner', 'desc')
    op.drop_column('banner', 'harga_jual')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('banner', sa.Column('harga_jual', mysql.BIGINT(display_width=20), autoincrement=False, nullable=True))
    op.add_column('banner', sa.Column('desc', mysql.VARCHAR(length=384), nullable=True))
    op.add_column('banner', sa.Column('harga_asli', mysql.BIGINT(display_width=20), autoincrement=False, nullable=True))
    op.drop_column('banner', 'body')
    # ### end Alembic commands ###

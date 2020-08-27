"""empty message

Revision ID: 4c9fac0b432f
Revises: 
Create Date: 2020-07-13 03:21:43.841240

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4c9fac0b432f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('password', sa.String(length=255), nullable=True),
    sa.Column('public_id', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('weather',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('city_name', sa.String(length=30), nullable=True),
    sa.Column('temperature', sa.Float(), nullable=True),
    sa.Column('humidity', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('weather')
    op.drop_table('user')
    # ### end Alembic commands ###

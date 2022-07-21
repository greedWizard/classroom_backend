"""change profile_photo on profile_photo_id

Revision ID: be54d92e8360
Revises: 160c65de6723
Create Date: 2022-07-20 19:21:32.189772

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'be54d92e8360'
down_revision = '160c65de6723'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('profile_photo_id', sa.Integer(), nullable=True))
    op.drop_column('users', 'profile_photo')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('profile_photo', postgresql.BYTEA(), autoincrement=False, nullable=True))
    op.drop_column('users', 'profile_photo_id')
    # ### end Alembic commands ###

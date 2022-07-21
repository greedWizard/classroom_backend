"""Add profile_photo column

Revision ID: 160c65de6723
Revises: 6df9b833bf68
Create Date: 2022-07-18 20:05:01.546911

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '160c65de6723'
down_revision = '6df9b833bf68'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('profile_photo', sa.LargeBinary(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'profile_photo')
    # ### end Alembic commands ###

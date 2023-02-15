"""added user avatar field

Revision ID: c62255c9c6a3
Revises: 6df9b833bf68
Create Date: 2022-07-25 18:58:58.174771

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c62255c9c6a3'
down_revision = '6df9b833bf68'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('profile_picture_id', sa.Integer(), nullable=True))
    op.create_unique_constraint(None, 'users', ['profile_picture_id'])
    op.create_foreign_key(None, 'users', 'attachments', ['profile_picture_id'], ['id'], ondelete='SET NULL', use_alter=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.drop_constraint(None, 'users', type_='unique')
    op.drop_column('users', 'profile_picture_id')
    # ### end Alembic commands ###

"""profile photo changes

Revision ID: 7ec92b5bb513
Revises: decd637dd08a
Create Date: 2023-03-07 21:11:17.002473

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7ec92b5bb513'
down_revision = 'decd637dd08a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('profile_picture_path', sa.String(), nullable=True))
    op.drop_constraint('users_profile_picture_id_key', 'users', type_='unique')
    op.drop_constraint('users_profile_picture_id_fkey', 'users', type_='foreignkey')
    op.drop_column('users', 'profile_picture_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('profile_picture_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('users_profile_picture_id_fkey', 'users', 'attachments', ['profile_picture_id'], ['id'], ondelete='SET NULL')
    op.create_unique_constraint('users_profile_picture_id_key', 'users', ['profile_picture_id'])
    op.drop_column('users', 'profile_picture_path')
    # ### end Alembic commands ###

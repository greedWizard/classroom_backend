"""allow delete on users table

Revision ID: 6df9b833bf68
Revises: 33f8bbd1dcb2
Create Date: 2022-07-15 18:50:52.985731

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6df9b833bf68'
down_revision = '33f8bbd1dcb2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('participations_user_id_fkey', 'participations', type_='foreignkey')
    op.create_foreign_key(None, 'participations', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'participations', type_='foreignkey')
    op.create_foreign_key('participations_user_id_fkey', 'participations', 'users', ['user_id'], ['id'])
    # ### end Alembic commands ###

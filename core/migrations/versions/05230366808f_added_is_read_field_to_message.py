"""Added is_read field to message

Revision ID: 05230366808f
Revises: 7527bb16606d
Create Date: 2022-08-28 20:50:03.366205

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '05230366808f'
down_revision = '7527bb16606d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('messages', sa.Column('is_read', sa.Boolean(), nullable=True, default=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('messages', 'is_read')
    # ### end Alembic commands ###

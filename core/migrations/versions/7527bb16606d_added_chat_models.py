"""added chat models

Revision ID: 7527bb16606d
Revises: 494cc696290e
Create Date: 2022-08-21 19:35:55.943226

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7527bb16606d'
down_revision = '494cc696290e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('dialogs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('author_id', sa.Integer(), nullable=False),
    sa.Column('updated_by_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['updated_by_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('dialogs_participants',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('dialog_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['dialog_id'], ['dialogs.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', 'dialog_id')
    )
    op.create_table('messages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('sender_id', sa.Integer(), nullable=False),
    sa.Column('dialog_id', sa.Integer(), nullable=False),
    sa.Column('text', sa.String(length=500), nullable=False),
    sa.ForeignKeyConstraint(['dialog_id'], ['dialogs.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('messages')
    op.drop_table('dialogs_participants')
    op.drop_table('dialogs')
    # ### end Alembic commands ###

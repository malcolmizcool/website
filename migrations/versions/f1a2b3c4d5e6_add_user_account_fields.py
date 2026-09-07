"""add user account fields for uandp.json migration

Revision ID: f1a2b3c4d5e6
Revises: c9a3bd5174e1
Create Date: 2026-09-07 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f1a2b3c4d5e6'
down_revision = 'c9a3bd5174e1'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('password', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('bio', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('pfp', sa.String(), nullable=True, server_default='None'))
        batch_op.add_column(sa.Column('role', sa.String(), nullable=True, server_default='user'))
        batch_op.add_column(sa.Column('accountDate', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('verified', sa.Boolean(), nullable=True, server_default=sa.false()))
        batch_op.add_column(sa.Column('lastSeen', sa.String(), nullable=True))


def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('lastSeen')
        batch_op.drop_column('verified')
        batch_op.drop_column('accountDate')
        batch_op.drop_column('role')
        batch_op.drop_column('pfp')
        batch_op.drop_column('bio')
        batch_op.drop_column('password')

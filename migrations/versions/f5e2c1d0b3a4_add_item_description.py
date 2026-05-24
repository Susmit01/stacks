"""add item description

Revision ID: f5e2c1d0b3a4
Revises: d8f3a9b1c2e5
Create Date: 2026-05-23 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'f5e2c1d0b3a4'
down_revision = 'd8f3a9b1c2e5'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('items', sa.Column('description', sa.Text(), nullable=True))


def downgrade():
    with op.batch_alter_table('items') as batch_op:
        batch_op.drop_column('description')

"""add groups

Revision ID: d8f3a9b1c2e5
Revises: cf0cde4cc5f0
Create Date: 2026-05-23 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'd8f3a9b1c2e5'
down_revision = 'cf0cde4cc5f0'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'groups',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('board_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('color', sa.String(length=7), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('collapsed', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['board_id'], ['boards.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )

    op.add_column('items', sa.Column('group_id', sa.Integer(), nullable=True))

    # Data migration: for each board create a default group, assign all items to it
    conn = op.get_bind()
    boards = conn.execute(sa.text('SELECT id FROM boards')).fetchall()
    for (board_id,) in boards:
        result = conn.execute(
            sa.text(
                "INSERT INTO groups (board_id, name, color, position, collapsed) "
                "VALUES (:bid, 'Items', '#0049b7', 0, 0)"
            ),
            {'bid': board_id}
        )
        group_id = result.lastrowid
        conn.execute(
            sa.text('UPDATE items SET group_id = :gid WHERE board_id = :bid'),
            {'gid': group_id, 'bid': board_id}
        )


def downgrade():
    with op.batch_alter_table('items') as batch_op:
        batch_op.drop_column('group_id')
    op.drop_table('groups')

"""add_advanced_todo_features

Revision ID: 79830b5c56cc
Revises:
Create Date: 2026-02-09 09:43:44.162967

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '79830b5c56cc'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add advanced todo features to existing schema."""

    # Note: The database already has tasks, tags, and task_tags tables
    # We only need to add missing columns

    # Add user_id to tags table (CRITICAL for user isolation security)
    # Note: SQLite doesn't support adding foreign keys after table creation
    # Foreign key enforcement will be handled at the application level
    op.add_column('tags', sa.Column('user_id', sa.String(36), nullable=True))
    op.create_index('ix_tags_user_id', 'tags', ['user_id'])

    # Add recurring task fields to tasks table
    op.add_column('tasks', sa.Column('is_recurring', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('tasks', sa.Column('recurrence_frequency', sa.String(10), nullable=True))
    op.add_column('tasks', sa.Column('last_recurrence_date', sa.Date(), nullable=True))

    # Note: SQLite has limited support for CHECK constraints in ALTER TABLE
    # Constraints will be enforced at the application level

    # Note: The following already exist in the database and don't need to be added:
    # - tasks.priority (exists as INTEGER)
    # - tasks.due_date (exists as DATETIME)
    # - tasks.completed (exists as BOOLEAN, equivalent to is_completed)
    # - tags table (exists)
    # - task_tags table (exists)


def downgrade() -> None:
    """Downgrade schema - Remove advanced todo features."""

    # Drop columns from tasks table
    op.drop_column('tasks', 'last_recurrence_date')
    op.drop_column('tasks', 'recurrence_frequency')
    op.drop_column('tasks', 'is_recurring')

    # Drop user_id from tags table
    op.drop_index('ix_tags_user_id', 'tags')
    op.drop_column('tags', 'user_id')

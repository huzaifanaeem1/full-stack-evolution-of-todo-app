# T050-T059: Recurring Task Service Business Logic
# Phase V - Part B: Event-Driven Architecture with Kafka and Dapr

"""
Recurring Task Service - Business logic for creating next recurring task instances.

This service:
- Checks if task is recurring
- Calculates next due date based on recurrence frequency
- Creates new task instance with preserved metadata
- Implements idempotency using last_recurrence_date
- Handles database transactions atomically
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from ..config.database import AsyncSessionLocal

logger = logging.getLogger(__name__)


# Task model (simplified for recurring task service)
# We'll use raw SQL/SQLAlchemy instead of importing from backend
# to maintain service independence


class RecurringTaskService:
    """
    Service for processing task.completed events and creating recurring task instances.
    """

    def __init__(self):
        self.db = None

    async def close(self):
        """Close database session."""
        if self.db:
            await self.db.close()

    async def process_task_completed_event(self, event_data: Dict[str, Any]) -> None:
        """
        T050-T059: Process task.completed event and create next recurring instance.

        Args:
            event_data: Event payload with task data

        Raises:
            Exception: For transient failures (database errors)
        """
        task_data = event_data["task"]
        user_id = UUID(event_data["user_id"])
        event_id = event_data["event_id"]

        # T051: Check if task is recurring
        if not self._is_recurring(task_data):
            logger.info(f"Task {task_data['id']} is not recurring, skipping")
            return

        # Get database session
        self.db = AsyncSessionLocal()

        try:
            # T056: Idempotency check using last_recurrence_date
            if await self._is_duplicate_event(task_data, event_id):
                logger.info(
                    f"Event {event_id} already processed for task {task_data['id']}, skipping"
                )
                return

            # T052-T054: Calculate next due date
            next_due_date = self._calculate_next_due_date(
                task_data["due_date"], task_data["recurrence_frequency"]
            )

            # T055: Create next task instance
            new_task_id = await self._create_next_task_instance(
                task_data, user_id, next_due_date
            )

            # T057: Update original task's last_recurrence_date (atomic transaction)
            await self._update_last_recurrence_date(
                UUID(task_data["id"]), next_due_date
            )

            # T057: Commit transaction
            await self.db.commit()

            logger.info(
                f"Created next recurring task instance: {new_task_id} "
                f"for original task {task_data['id']}"
            )

        except IntegrityError as e:
            # T058: Handle database errors
            await self.db.rollback()
            logger.error(f"Database integrity error: {str(e)}")
            raise

        except Exception as e:
            # T058: Handle transient failures
            await self.db.rollback()
            logger.error(f"Error creating recurring task instance: {str(e)}")
            raise

    def _is_recurring(self, task_data: Dict[str, Any]) -> bool:
        """
        T051: Check if task is recurring.

        Args:
            task_data: Task data from event

        Returns:
            True if task is recurring, False otherwise
        """
        return (
            task_data.get("is_recurring", False)
            and task_data.get("recurrence_frequency") is not None
            and task_data.get("due_date") is not None
        )

    def _calculate_next_due_date(
        self, current_due_date: str, frequency: str
    ) -> date:
        """
        T052-T054: Calculate next due date based on recurrence frequency.

        Clarification: For monthly recurring tasks, use same day next month,
        capped at month end (e.g., Jan 31 → Feb 28/29).

        Args:
            current_due_date: ISO8601 date string
            frequency: Recurrence frequency (daily, weekly, monthly)

        Returns:
            Next due date
        """
        # Parse current due date
        if isinstance(current_due_date, str):
            current_date = datetime.fromisoformat(
                current_due_date.replace("Z", "+00:00")
            ).date()
        else:
            current_date = current_due_date

        # T052: Daily frequency
        if frequency == "daily":
            return current_date + timedelta(days=1)

        # T053: Weekly frequency
        elif frequency == "weekly":
            return current_date + timedelta(weeks=1)

        # T054: Monthly frequency with edge case handling
        elif frequency == "monthly":
            # Clarification: Same day next month, capped at month end
            # Use dateutil.relativedelta for proper month arithmetic
            next_date = current_date + relativedelta(months=1)
            return next_date

        else:
            raise ValueError(f"Invalid recurrence frequency: {frequency}")

    async def _is_duplicate_event(
        self, task_data: Dict[str, Any], event_id: str
    ) -> bool:
        """
        T056: Check if event has already been processed (idempotency).

        Uses last_recurrence_date to prevent duplicate task creation.

        Args:
            task_data: Task data from event
            event_id: Event ID for logging

        Returns:
            True if event already processed, False otherwise
        """
        task_id = UUID(task_data["id"])

        # Query task's last_recurrence_date
        query = select(
            "last_recurrence_date"
        ).select_from(
            "tasks"
        ).where(
            "id = :task_id"
        )

        # Use raw SQL for simplicity (avoiding model imports)
        result = await self.db.execute(
            f"SELECT last_recurrence_date FROM tasks WHERE id = '{task_id}'"
        )
        row = result.fetchone()

        if not row or row[0] is None:
            # No last_recurrence_date, first time processing
            return False

        last_recurrence_date = row[0]

        # Calculate what the next due date would be
        next_due_date = self._calculate_next_due_date(
            task_data["due_date"], task_data["recurrence_frequency"]
        )

        # If last_recurrence_date >= next_due_date, already processed
        if last_recurrence_date >= next_due_date:
            return True

        return False

    async def _create_next_task_instance(
        self, task_data: Dict[str, Any], user_id: UUID, next_due_date: date
    ) -> UUID:
        """
        T055: Create new task instance with preserved metadata.

        Args:
            task_data: Original task data
            user_id: User ID
            next_due_date: Calculated next due date

        Returns:
            New task ID
        """
        # Generate new task ID
        import uuid
        new_task_id = uuid.uuid4()

        # T055, T022: Preserve task metadata (title, description, priority, tags)
        # T023: Set new task to incomplete status
        insert_query = """
        INSERT INTO tasks (
            id, user_id, title, description, is_completed,
            priority, due_date, is_recurring, recurrence_frequency,
            created_at, updated_at
        ) VALUES (
            :id, :user_id, :title, :description, :is_completed,
            :priority, :due_date, :is_recurring, :recurrence_frequency,
            :created_at, :updated_at
        )
        """

        now = datetime.utcnow()

        await self.db.execute(
            insert_query,
            {
                "id": str(new_task_id),
                "user_id": str(user_id),
                "title": task_data["title"],
                "description": task_data.get("description", ""),
                "is_completed": False,  # T023: New instance starts incomplete
                "priority": task_data.get("priority", "medium"),
                "due_date": next_due_date,
                "is_recurring": task_data["is_recurring"],
                "recurrence_frequency": task_data["recurrence_frequency"],
                "created_at": now,
                "updated_at": now,
            },
        )

        # T055: Copy tags to new instance (if tags exist)
        if task_data.get("tags"):
            await self._copy_tags_to_new_task(
                UUID(task_data["id"]), new_task_id, user_id
            )

        # T059: Log task creation
        logger.info(
            f"Created new recurring task instance: {new_task_id} "
            f"with due date {next_due_date}"
        )

        return new_task_id

    async def _copy_tags_to_new_task(
        self, original_task_id: UUID, new_task_id: UUID, user_id: UUID
    ) -> None:
        """
        Copy tags from original task to new recurring instance.

        Args:
            original_task_id: Original task ID
            new_task_id: New task ID
            user_id: User ID
        """
        # Get tags from original task
        query = """
        SELECT t.id, t.name
        FROM tags t
        JOIN task_tags tt ON t.id = tt.tag_id
        WHERE tt.task_id = :original_task_id
        """

        result = await self.db.execute(query, {"original_task_id": str(original_task_id)})
        tags = result.fetchall()

        # Copy tags to new task
        for tag_id, tag_name in tags:
            insert_query = """
            INSERT INTO task_tags (task_id, tag_id)
            VALUES (:task_id, :tag_id)
            ON CONFLICT DO NOTHING
            """
            await self.db.execute(
                insert_query,
                {"task_id": str(new_task_id), "tag_id": tag_id}
            )

    async def _update_last_recurrence_date(
        self, task_id: UUID, next_due_date: date
    ) -> None:
        """
        T057: Update original task's last_recurrence_date for idempotency.

        Args:
            task_id: Original task ID
            next_due_date: Next due date to record
        """
        update_query = """
        UPDATE tasks
        SET last_recurrence_date = :next_due_date, updated_at = :updated_at
        WHERE id = :task_id
        """

        await self.db.execute(
            update_query,
            {
                "task_id": str(task_id),
                "next_due_date": next_due_date,
                "updated_at": datetime.utcnow(),
            },
        )

        logger.info(
            f"Updated last_recurrence_date for task {task_id} to {next_due_date}"
        )

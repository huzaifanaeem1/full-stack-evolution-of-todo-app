# T047-T049: Task Completed Event Handler
# Phase V - Part B: Event-Driven Architecture with Kafka and Dapr

"""
Handler for task.completed events from Dapr.

This handler:
- Validates event schema
- Parses event data
- Delegates to RecurringTaskService for business logic
"""

import logging
from typing import Dict, Any

from ..services.recurring_task_service import RecurringTaskService
from ..config.dapr import EVENT_TYPE_TASK_COMPLETED

logger = logging.getLogger(__name__)


async def handle_task_completed(event_data: Dict[str, Any]) -> None:
    """
    T047-T049: Handle task.completed event.

    Args:
        event_data: Event payload from Dapr

    Raises:
        ValueError: If event schema is invalid (permanent failure)
        Exception: For transient failures (database errors, etc.)
    """
    # T048: Validate event schema
    if not event_data:
        raise ValueError("Empty event data")

    # Extract event fields
    event_id = event_data.get("id")
    event_type = event_data.get("type")

    # Dapr wraps the event, extract the actual data
    if "data" in event_data:
        data = event_data["data"]
    else:
        data = event_data

    # Validate required fields
    if not data.get("event_id"):
        raise ValueError("Missing event_id in event data")

    if not data.get("event_type"):
        raise ValueError("Missing event_type in event data")

    if data.get("event_type") != EVENT_TYPE_TASK_COMPLETED:
        # Not a task.completed event, skip processing
        logger.info(f"Skipping non-completed event: {data.get('event_type')}")
        return

    if not data.get("user_id"):
        raise ValueError("Missing user_id in event data")

    if not data.get("task"):
        raise ValueError("Missing task data in event")

    task_data = data["task"]

    # Validate task fields
    if not task_data.get("id"):
        raise ValueError("Missing task.id in event data")

    if not task_data.get("is_recurring"):
        # Not a recurring task, skip processing
        logger.info(f"Skipping non-recurring task: {task_data.get('id')}")
        return

    # T049: Delegate to RecurringTaskService
    service = RecurringTaskService()
    try:
        await service.process_task_completed_event(data)
        logger.info(
            f"Successfully processed task.completed event: {data.get('event_id')}"
        )
    finally:
        await service.close()

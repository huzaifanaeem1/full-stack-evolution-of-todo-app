# T074-T076: Reminder Event Handler
# Phase V - Part B: Event-Driven Architecture with Kafka and Dapr

"""
Handler for reminder events from Dapr.

This handler:
- Validates event schema
- Parses event data
- Delegates to NotificationService for logging
"""

import logging
from typing import Dict, Any

from ..services.notification_service import NotificationService
from ..config.dapr import EVENT_TYPE_REMINDER_DUE_SOON

logger = logging.getLogger(__name__)


async def handle_reminder(event_data: Dict[str, Any]) -> None:
    """
    T074-T076: Handle reminder event.

    Args:
        event_data: Event payload from Dapr

    Raises:
        ValueError: If event schema is invalid (permanent failure)
        Exception: For transient failures
    """
    # T075: Validate event schema
    if not event_data:
        raise ValueError("Empty event data")

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

    if data.get("event_type") != EVENT_TYPE_REMINDER_DUE_SOON:
        # Not a reminder.due_soon event, skip processing
        logger.info(f"Skipping non-reminder event: {data.get('event_type')}")
        return

    if not data.get("user_id"):
        raise ValueError("Missing user_id in event data")

    if not data.get("task"):
        raise ValueError("Missing task data in event")

    task_data = data["task"]

    # Validate task fields
    if not task_data.get("id"):
        raise ValueError("Missing task.id in event data")

    if not task_data.get("title"):
        raise ValueError("Missing task.title in event data")

    if not task_data.get("due_date"):
        raise ValueError("Missing task.due_date in event data")

    if not data.get("reminder_type"):
        raise ValueError("Missing reminder_type in event data")

    # T076: Delegate to NotificationService
    service = NotificationService()
    await service.log_notification(data)

    logger.info(
        f"Successfully processed reminder event: {data.get('event_id')}"
    )

# T077-T082: Notification Service Business Logic
# Phase V - Part B: Event-Driven Architecture with Kafka and Dapr

"""
Notification Service - Business logic for logging reminder notifications.

This service:
- Logs notifications to console with structured format
- Implements idempotency using in-memory event_id tracking
- Handles duplicate reminder events safely
"""

import logging
from typing import Dict, Any, Set
from datetime import datetime, timedelta
from collections import OrderedDict

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service for logging reminder notifications to console.

    Implements idempotency using in-memory event_id tracking with TTL.
    """

    # T079: In-memory event_id tracking (class-level, shared across instances)
    # Store last 10,000 events with timestamps
    _processed_events: OrderedDict[str, datetime] = OrderedDict()
    _max_events = 10000
    _ttl_hours = 1  # T080: 1-hour TTL

    def __init__(self):
        pass

    async def log_notification(self, event_data: Dict[str, Any]) -> None:
        """
        T078, T082: Log notification to console with task details and user_id.

        Args:
            event_data: Event payload with reminder data
        """
        event_id = event_data["event_id"]

        # T079: Check if event already processed (idempotency)
        if self._is_duplicate_event(event_id):
            logger.info(
                f"Duplicate reminder event detected: {event_id}, skipping notification"
            )
            return

        # T080: Clean up expired events before adding new one
        self._cleanup_expired_events()

        # Extract event data
        user_id = event_data["user_id"]
        task_data = event_data["task"]
        reminder_type = event_data["reminder_type"]

        # T078, T082: Log notification with structured format
        notification_message = (
            f"[REMINDER] {reminder_type} | "
            f"User: {user_id} | "
            f"Task: {task_data['title']} | "
            f"Due: {task_data['due_date']} | "
            f"Priority: {task_data.get('priority', 'medium')}"
        )

        logger.info(notification_message)

        # T079: Track processed event_id
        self._processed_events[event_id] = datetime.utcnow()

        # T079: Maintain max size (last 10,000 events)
        if len(self._processed_events) > self._max_events:
            # Remove oldest event
            self._processed_events.popitem(last=False)

        # T082: Log additional details for debugging
        logger.debug(
            f"Notification logged for event {event_id}: "
            f"task_id={task_data['id']}, "
            f"reminder_type={reminder_type}"
        )

    def _is_duplicate_event(self, event_id: str) -> bool:
        """
        T079: Check if event has already been processed.

        Args:
            event_id: Event ID to check

        Returns:
            True if event already processed, False otherwise
        """
        if event_id in self._processed_events:
            # Check if event is still within TTL
            processed_time = self._processed_events[event_id]
            age = datetime.utcnow() - processed_time

            if age < timedelta(hours=self._ttl_hours):
                return True
            else:
                # Event expired, remove it
                del self._processed_events[event_id]
                return False

        return False

    def _cleanup_expired_events(self) -> None:
        """
        T080: Clean up expired events from tracking (TTL-based expiration).

        Removes events older than 1 hour.
        """
        now = datetime.utcnow()
        expired_keys = []

        for event_id, processed_time in self._processed_events.items():
            age = now - processed_time
            if age >= timedelta(hours=self._ttl_hours):
                expired_keys.append(event_id)
            else:
                # OrderedDict maintains insertion order, so once we hit
                # a non-expired event, all subsequent events are also non-expired
                break

        # Remove expired events
        for event_id in expired_keys:
            del self._processed_events[event_id]

        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired events from tracking")

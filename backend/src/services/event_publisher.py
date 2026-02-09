# T023-T030: EventPublisher Service
# Phase V - Part B: Event-Driven Architecture with Kafka and Dapr

"""
Event Publisher service for publishing task lifecycle events to Kafka via Dapr.

This service handles:
- Event schema building for task.created, task.updated, task.completed, task.deleted
- Event ID generation (UUID) for idempotency
- Asynchronous event publishing via Dapr HTTP API
- Error handling and logging for publishing failures
- Event buffering and automatic retry when Kafka is unavailable
"""

import uuid
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
import httpx
import asyncio
from collections import deque

from ..config.dapr import (
    get_publish_url,
    TOPIC_TASK_EVENTS,
    EVENT_TYPE_TASK_CREATED,
    EVENT_TYPE_TASK_UPDATED,
    EVENT_TYPE_TASK_COMPLETED,
    EVENT_TYPE_TASK_DELETED,
)
from ..models.task import Task

# Configure logging
logger = logging.getLogger(__name__)

# Event buffer for retry when Kafka is unavailable (clarification: buffer in memory and retry)
event_buffer: deque = deque(maxlen=1000)  # Max 1000 events in buffer
retry_task: Optional[asyncio.Task] = None


class EventPublisher:
    """
    Service for publishing task lifecycle events to Kafka via Dapr Pub/Sub.
    """

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=5.0)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    def _generate_event_id(self) -> str:
        """
        T029: Generate unique event ID (UUID v4) for idempotency.

        Returns:
            UUID string for event identification
        """
        return str(uuid.uuid4())

    def _get_current_timestamp(self) -> str:
        """
        Get current timestamp in ISO8601 format.

        Returns:
            ISO8601 formatted timestamp string
        """
        return datetime.utcnow().isoformat() + "Z"

    def _build_task_event_payload(
        self, event_type: str, task: Task, user_id: UUID
    ) -> Dict[str, Any]:
        """
        Build event payload with complete task metadata.

        Args:
            event_type: Type of event (task.created, task.updated, etc.)
            task: Task object with all metadata
            user_id: UUID of the user who owns the task

        Returns:
            Complete event payload dictionary
        """
        return {
            "event_id": self._generate_event_id(),
            "event_type": event_type,
            "event_timestamp": self._get_current_timestamp(),
            "user_id": str(user_id),
            "task": {
                "id": str(task.id),
                "title": task.title,
                "description": task.description or "",
                "is_completed": task.is_completed,
                "priority": task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "is_recurring": task.is_recurring,
                "recurrence_frequency": task.recurrence_frequency,
                "tags": getattr(task, "tags", []),  # Tags populated by service layer
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "updated_at": task.updated_at.isoformat() if task.updated_at else None,
            },
        }

    def _build_task_created_event(self, task: Task, user_id: UUID) -> Dict[str, Any]:
        """
        T025: Build event schema for task.created events.

        Args:
            task: Newly created task
            user_id: UUID of the user who created the task

        Returns:
            task.created event payload
        """
        return self._build_task_event_payload(EVENT_TYPE_TASK_CREATED, task, user_id)

    def _build_task_updated_event(self, task: Task, user_id: UUID) -> Dict[str, Any]:
        """
        T026: Build event schema for task.updated events.

        Args:
            task: Updated task
            user_id: UUID of the user who updated the task

        Returns:
            task.updated event payload
        """
        return self._build_task_event_payload(EVENT_TYPE_TASK_UPDATED, task, user_id)

    def _build_task_completed_event(self, task: Task, user_id: UUID) -> Dict[str, Any]:
        """
        T027: Build event schema for task.completed events.

        Args:
            task: Completed task
            user_id: UUID of the user who completed the task

        Returns:
            task.completed event payload
        """
        return self._build_task_event_payload(EVENT_TYPE_TASK_COMPLETED, task, user_id)

    def _build_task_deleted_event(self, task: Task, user_id: UUID) -> Dict[str, Any]:
        """
        T028: Build event schema for task.deleted events.

        Args:
            task: Deleted task
            user_id: UUID of the user who deleted the task

        Returns:
            task.deleted event payload
        """
        return self._build_task_event_payload(EVENT_TYPE_TASK_DELETED, task, user_id)

    async def _publish_event(self, event_payload: Dict[str, Any]) -> bool:
        """
        T024: Publish event to Dapr HTTP API with error handling.

        Args:
            event_payload: Complete event payload to publish

        Returns:
            True if published successfully, False otherwise
        """
        try:
            url = get_publish_url(TOPIC_TASK_EVENTS)
            response = await self.client.post(url, json=event_payload)

            if response.status_code in [200, 204]:
                logger.info(
                    f"Event published successfully: {event_payload['event_type']} "
                    f"(event_id: {event_payload['event_id']})"
                )
                return True
            else:
                logger.error(
                    f"Failed to publish event: {event_payload['event_type']} "
                    f"(status: {response.status_code}, event_id: {event_payload['event_id']})"
                )
                return False

        except httpx.ConnectError as e:
            # T030: Dapr sidecar unavailable - buffer and retry
            logger.warning(
                f"Dapr sidecar unavailable, buffering event: {event_payload['event_type']} "
                f"(event_id: {event_payload['event_id']}) - {str(e)}"
            )
            return False

        except Exception as e:
            # T030: Log all other errors
            logger.error(
                f"Unexpected error publishing event: {event_payload['event_type']} "
                f"(event_id: {event_payload['event_id']}) - {str(e)}"
            )
            return False

    async def publish_task_event(
        self, event_type: str, task: Task, user_id: UUID
    ) -> None:
        """
        Publish task lifecycle event asynchronously without blocking.

        Clarification: Buffer events in memory and retry automatically until Kafka recovers.

        Args:
            event_type: Type of event to publish
            task: Task object
            user_id: UUID of the user
        """
        # Build event payload based on type
        if event_type == EVENT_TYPE_TASK_CREATED:
            event_payload = self._build_task_created_event(task, user_id)
        elif event_type == EVENT_TYPE_TASK_UPDATED:
            event_payload = self._build_task_updated_event(task, user_id)
        elif event_type == EVENT_TYPE_TASK_COMPLETED:
            event_payload = self._build_task_completed_event(task, user_id)
        elif event_type == EVENT_TYPE_TASK_DELETED:
            event_payload = self._build_task_deleted_event(task, user_id)
        else:
            logger.error(f"Unknown event type: {event_type}")
            return

        # Attempt to publish
        success = await self._publish_event(event_payload)

        # If failed, buffer for retry (clarification: buffer in memory and retry)
        if not success:
            event_buffer.append(event_payload)
            logger.info(
                f"Event buffered for retry: {event_type} "
                f"(buffer size: {len(event_buffer)})"
            )
            # Start retry task if not already running
            await self._start_retry_task()

    async def _start_retry_task(self):
        """
        Start background task to retry buffered events.

        Clarification: Retry automatically until Kafka recovers.
        """
        global retry_task
        if retry_task is None or retry_task.done():
            retry_task = asyncio.create_task(self._retry_buffered_events())

    async def _retry_buffered_events(self):
        """
        Background task to retry publishing buffered events.

        Retries every 5 seconds until buffer is empty.
        """
        while len(event_buffer) > 0:
            await asyncio.sleep(5)  # Wait 5 seconds between retries

            # Try to publish all buffered events
            failed_events = []
            while len(event_buffer) > 0:
                event_payload = event_buffer.popleft()
                success = await self._publish_event(event_payload)

                if not success:
                    failed_events.append(event_payload)

            # Re-buffer failed events
            for event in failed_events:
                event_buffer.append(event)

            if len(failed_events) > 0:
                logger.warning(
                    f"Retry failed for {len(failed_events)} events, "
                    f"will retry again in 5 seconds"
                )
            else:
                logger.info("All buffered events published successfully")


# Global event publisher instance
_event_publisher: Optional[EventPublisher] = None


def get_event_publisher() -> EventPublisher:
    """
    Get or create the global EventPublisher instance.

    Returns:
        EventPublisher instance
    """
    global _event_publisher
    if _event_publisher is None:
        _event_publisher = EventPublisher()
    return _event_publisher


async def close_event_publisher():
    """
    Close the global EventPublisher instance.
    """
    global _event_publisher
    if _event_publisher is not None:
        await _event_publisher.close()
        _event_publisher = None

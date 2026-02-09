# T021: Dapr Configuration Module for Backend
# Phase V - Part B: Event-Driven Architecture with Kafka and Dapr

"""
Dapr configuration and constants for event publishing.
"""

from typing import Final

# Dapr sidecar configuration
DAPR_HTTP_PORT: Final[int] = 3500
DAPR_GRPC_PORT: Final[int] = 50001
DAPR_HOST: Final[str] = "localhost"

# Dapr Pub/Sub component name
PUBSUB_NAME: Final[str] = "pubsub-kafka"

# Event topics
TOPIC_TASK_EVENTS: Final[str] = "task-events"
TOPIC_REMINDERS: Final[str] = "reminders"

# Event types
EVENT_TYPE_TASK_CREATED: Final[str] = "task.created"
EVENT_TYPE_TASK_UPDATED: Final[str] = "task.updated"
EVENT_TYPE_TASK_COMPLETED: Final[str] = "task.completed"
EVENT_TYPE_TASK_DELETED: Final[str] = "task.deleted"
EVENT_TYPE_REMINDER_DUE_SOON: Final[str] = "reminder.due_soon"

# Dapr publish endpoint
def get_publish_url(topic: str) -> str:
    """
    Get the Dapr publish endpoint URL for a given topic.

    Args:
        topic: The topic name (e.g., "task-events", "reminders")

    Returns:
        Full URL for Dapr publish endpoint
    """
    return f"http://{DAPR_HOST}:{DAPR_HTTP_PORT}/v1.0/publish/{PUBSUB_NAME}/{topic}"


# Dapr health check endpoint
def get_health_url() -> str:
    """
    Get the Dapr health check endpoint URL.

    Returns:
        Full URL for Dapr health check
    """
    return f"http://{DAPR_HOST}:{DAPR_HTTP_PORT}/v1.0/healthz"

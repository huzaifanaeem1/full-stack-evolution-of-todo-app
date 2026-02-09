# T045: Dapr Configuration Module for Recurring Task Service
# Phase V - Part B: Event-Driven Architecture with Kafka and Dapr

"""
Dapr configuration and constants for Recurring Task Service.
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

# Event types
EVENT_TYPE_TASK_COMPLETED: Final[str] = "task.completed"

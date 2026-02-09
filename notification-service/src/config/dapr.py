# T073: Dapr Configuration Module for Notification Service
# Phase V - Part B: Event-Driven Architecture with Kafka and Dapr

"""
Dapr configuration and constants for Notification Service.
"""

from typing import Final

# Dapr sidecar configuration
DAPR_HTTP_PORT: Final[int] = 3500
DAPR_GRPC_PORT: Final[int] = 50001
DAPR_HOST: Final[str] = "localhost"

# Dapr Pub/Sub component name
PUBSUB_NAME: Final[str] = "pubsub-kafka"

# Event topics
TOPIC_REMINDERS: Final[str] = "reminders"

# Event types
EVENT_TYPE_REMINDER_DUE_SOON: Final[str] = "reminder.due_soon"

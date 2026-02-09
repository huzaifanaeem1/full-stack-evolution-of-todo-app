# T043-T044: Recurring Task Service Main Entry Point
# Phase V - Part B: Event-Driven Architecture with Kafka and Dapr

"""
Recurring Task Service - Consumer service for task.completed events.

This service:
- Subscribes to task-events topic via Dapr
- Consumes task.completed events
- Creates next recurring task instance based on recurrence frequency
- Implements idempotency to prevent duplicate task creation
"""

from fastapi import FastAPI, Request, Response
from typing import Dict, Any, List
import logging

from .handlers.task_completed_handler import handle_task_completed
from .config.dapr import PUBSUB_NAME, TOPIC_TASK_EVENTS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Recurring Task Service",
    description="Consumer service for recurring task automation",
    version="1.0.0"
)


@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes probes."""
    return {"status": "healthy", "service": "recurring-task-service"}


@app.get("/dapr/subscribe")
async def subscribe() -> List[Dict[str, Any]]:
    """
    T044: Dapr subscription endpoint.

    Returns subscription configuration for Dapr to register this service
    as a consumer of task-events topic.

    Returns:
        List of subscription configurations
    """
    subscriptions = [
        {
            "pubsubname": PUBSUB_NAME,
            "topic": TOPIC_TASK_EVENTS,
            "route": "/task-completed",
            "metadata": {
                "rawPayload": "false"
            }
        }
    ]

    logger.info(f"Dapr subscription registered: {subscriptions}")
    return subscriptions


@app.post("/task-completed")
async def task_completed_endpoint(request: Request):
    """
    T047-T049: Event handler endpoint for task.completed events.

    Dapr delivers events to this endpoint via HTTP POST.

    Returns:
        - 200 OK: Event processed successfully (Dapr commits offset)
        - 500 Internal Server Error: Transient failure (Dapr retries)
        - 400 Bad Request: Permanent failure (Dapr moves to DLQ)
    """
    try:
        # Parse event payload
        event_data = await request.json()

        logger.info(f"Received task.completed event: {event_data.get('id', 'unknown')}")

        # Handle the event
        await handle_task_completed(event_data)

        # Return 200 OK to commit offset
        return Response(status_code=200)

    except ValueError as e:
        # Permanent failure (invalid schema, missing fields)
        logger.error(f"Invalid event schema: {str(e)}")
        return Response(status_code=400, content=str(e))

    except Exception as e:
        # Transient failure (database error, network issue)
        logger.error(f"Error processing event: {str(e)}")
        return Response(status_code=500, content=str(e))


@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info("Recurring Task Service starting up...")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("Recurring Task Service shutting down...")

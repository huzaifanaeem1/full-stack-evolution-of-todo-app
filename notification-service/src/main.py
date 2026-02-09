# T071-T072: Notification Service Main Entry Point
# Phase V - Part B: Event-Driven Architecture with Kafka and Dapr

"""
Notification Service - Consumer service for reminder events.

This service:
- Subscribes to reminders topic via Dapr
- Consumes reminder events
- Logs notifications to console (console/log-based for this phase)
- Implements idempotency using in-memory event_id tracking
"""

from fastapi import FastAPI, Request, Response
from typing import Dict, Any, List
import logging

from .handlers.reminder_handler import handle_reminder
from .config.dapr import PUBSUB_NAME, TOPIC_REMINDERS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Notification Service",
    description="Consumer service for due date reminder notifications",
    version="1.0.0"
)


@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes probes."""
    return {"status": "healthy", "service": "notification-service"}


@app.get("/dapr/subscribe")
async def subscribe() -> List[Dict[str, Any]]:
    """
    T072: Dapr subscription endpoint.

    Returns subscription configuration for Dapr to register this service
    as a consumer of reminders topic.

    Returns:
        List of subscription configurations
    """
    subscriptions = [
        {
            "pubsubname": PUBSUB_NAME,
            "topic": TOPIC_REMINDERS,
            "route": "/reminder",
            "metadata": {
                "rawPayload": "false"
            }
        }
    ]

    logger.info(f"Dapr subscription registered: {subscriptions}")
    return subscriptions


@app.post("/reminder")
async def reminder_endpoint(request: Request):
    """
    T074-T076: Event handler endpoint for reminder events.

    Dapr delivers events to this endpoint via HTTP POST.

    Returns:
        - 200 OK: Event processed successfully (Dapr commits offset)
        - 500 Internal Server Error: Transient failure (Dapr retries)
        - 400 Bad Request: Permanent failure (Dapr moves to DLQ)
    """
    try:
        # Parse event payload
        event_data = await request.json()

        logger.info(f"Received reminder event: {event_data.get('id', 'unknown')}")

        # Handle the event
        await handle_reminder(event_data)

        # Return 200 OK to commit offset
        return Response(status_code=200)

    except ValueError as e:
        # Permanent failure (invalid schema, missing fields)
        logger.error(f"Invalid event schema: {str(e)}")
        return Response(status_code=400, content=str(e))

    except Exception as e:
        # Transient failure (network issue, etc.)
        logger.error(f"Error processing event: {str(e)}")
        return Response(status_code=500, content=str(e))


@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info("Notification Service starting up...")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("Notification Service shutting down...")

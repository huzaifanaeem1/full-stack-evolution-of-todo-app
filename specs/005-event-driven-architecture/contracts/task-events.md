# T019: Task Events Contract Documentation
# Phase V - Part B: Event-Driven Architecture with Kafka and Dapr

## Task Events Topic Contract

**Topic Name**: `task-events`

**Purpose**: Publish all task lifecycle events to enable asynchronous processing by downstream consumer services.

**Producer**: Chat API Service (backend)

**Consumers**:
- Recurring Task Service (consumes `task.completed` events)
- Future consumers can subscribe to any event type

---

## Event Types

### 1. task.created

**Trigger**: When a user creates a new task

**Schema**:
```json
{
  "event_id": "uuid",
  "event_type": "task.created",
  "event_timestamp": "ISO8601",
  "user_id": "uuid",
  "task": {
    "id": "uuid",
    "title": "string",
    "description": "string",
    "is_completed": false,
    "priority": "high | medium | low",
    "due_date": "ISO8601 | null",
    "is_recurring": "boolean",
    "recurrence_frequency": "daily | weekly | monthly | null",
    "tags": ["string"],
    "created_at": "ISO8601",
    "updated_at": "ISO8601"
  }
}
```

**Validation Rules**:
- `event_id` must be a valid UUID v4
- `event_type` must be exactly "task.created"
- `user_id` must be a valid UUID and match the authenticated user
- `task.id` must be a valid UUID
- `task.is_completed` must be false for new tasks
- `task.created_at` and `task.updated_at` must be identical for new tasks

---

### 2. task.updated

**Trigger**: When a user updates an existing task (title, description, priority, due_date, tags)

**Schema**:
```json
{
  "event_id": "uuid",
  "event_type": "task.updated",
  "event_timestamp": "ISO8601",
  "user_id": "uuid",
  "task": {
    "id": "uuid",
    "title": "string",
    "description": "string",
    "is_completed": "boolean",
    "priority": "high | medium | low",
    "due_date": "ISO8601 | null",
    "is_recurring": "boolean",
    "recurrence_frequency": "daily | weekly | monthly | null",
    "tags": ["string"],
    "created_at": "ISO8601",
    "updated_at": "ISO8601"
  }
}
```

**Validation Rules**:
- `event_id` must be a valid UUID v4
- `event_type` must be exactly "task.updated"
- `user_id` must be a valid UUID and match the task owner
- `task.updated_at` must be more recent than `task.created_at`

---

### 3. task.completed

**Trigger**: When a user marks a task as completed

**Schema**:
```json
{
  "event_id": "uuid",
  "event_type": "task.completed",
  "event_timestamp": "ISO8601",
  "user_id": "uuid",
  "task": {
    "id": "uuid",
    "title": "string",
    "description": "string",
    "is_completed": true,
    "priority": "high | medium | low",
    "due_date": "ISO8601 | null",
    "is_recurring": "boolean",
    "recurrence_frequency": "daily | weekly | monthly | null",
    "tags": ["string"],
    "created_at": "ISO8601",
    "updated_at": "ISO8601"
  }
}
```

**Validation Rules**:
- `event_id` must be a valid UUID v4
- `event_type` must be exactly "task.completed"
- `user_id` must be a valid UUID and match the task owner
- `task.is_completed` must be true

**Consumer Behavior** (Recurring Task Service):
- If `task.is_recurring` is true, create next task instance
- Calculate next due date based on `task.recurrence_frequency`
- Preserve task metadata (title, description, priority, tags)
- Set new task to incomplete status

---

### 4. task.deleted

**Trigger**: When a user deletes a task

**Schema**:
```json
{
  "event_id": "uuid",
  "event_type": "task.deleted",
  "event_timestamp": "ISO8601",
  "user_id": "uuid",
  "task": {
    "id": "uuid",
    "title": "string",
    "description": "string",
    "is_completed": "boolean",
    "priority": "high | medium | low",
    "due_date": "ISO8601 | null",
    "is_recurring": "boolean",
    "recurrence_frequency": "daily | weekly | monthly | null",
    "tags": ["string"],
    "created_at": "ISO8601",
    "updated_at": "ISO8601"
  }
}
```

**Validation Rules**:
- `event_id` must be a valid UUID v4
- `event_type` must be exactly "task.deleted"
- `user_id` must be a valid UUID and match the task owner

---

## Publishing Requirements

### Producer Responsibilities

1. **Event ID Generation**: Generate unique UUID v4 for each event
2. **Timestamp**: Use ISO8601 format with timezone (UTC recommended)
3. **User ID**: Extract from JWT token, never trust client input
4. **Complete Task Data**: Include all task fields in event payload
5. **Asynchronous Publishing**: Never block user requests on event publishing
6. **Error Handling**: Log failures, continue with user operation

### Publishing Endpoint

**Dapr HTTP API**:
```
POST http://localhost:3500/v1.0/publish/pubsub-kafka/task-events
Content-Type: application/json

{event payload}
```

### Failure Handling

- **Kafka Unavailable**: Buffer events in memory and retry automatically
- **Publishing Failure**: Log error, do not fail user operation
- **Dapr Sidecar Down**: Log error, continue with user operation

---

## Consumption Requirements

### Consumer Responsibilities

1. **Idempotency**: Handle duplicate events safely (at-least-once delivery)
2. **User ID Validation**: Verify user_id exists and is valid
3. **Event ID Tracking**: Track processed event_ids to prevent duplicates
4. **Error Handling**: Retry transient failures, log permanent failures
5. **Offset Management**: Commit offsets only after successful processing

### Subscription Configuration

Consumers must implement `/dapr/subscribe` endpoint returning:
```json
[
  {
    "pubsubname": "pubsub-kafka",
    "topic": "task-events",
    "route": "/task-completed",
    "metadata": {
      "rawPayload": "false"
    }
  }
]
```

### Event Handler Response Codes

- **200 OK**: Event processed successfully, commit offset
- **500 Internal Server Error**: Transient failure, retry event
- **400 Bad Request**: Permanent failure, move to dead letter queue

---

## Testing

### Test Scenarios

1. **Event Publishing**: Create/update/complete/delete task, verify event published
2. **Event Schema**: Validate all required fields present and correctly formatted
3. **Idempotency**: Publish duplicate event, verify consumer handles it safely
4. **Failure Handling**: Stop Kafka, verify user operations still succeed
5. **Consumer Processing**: Complete recurring task, verify next instance created

### Test Tools

- Kafka CLI tools: `kafka-console-consumer` to inspect events
- Dapr CLI: `dapr run` for local testing
- kubectl logs: View consumer processing logs in Kubernetes

---

## Monitoring

### Key Metrics

- Event publishing rate (events/second)
- Event publishing latency (p50, p95, p99)
- Event publishing failures (count, rate)
- Consumer lag (events behind)
- Consumer processing latency (p50, p95, p99)

### Logging

All events must be logged with:
- Event ID
- Event type
- User ID
- Timestamp
- Success/failure status

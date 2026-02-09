# T018: Event Schema Documentation
# Phase V - Part B: Event-Driven Architecture with Kafka and Dapr

## Event Schemas and Data Structures

This document defines the event schemas used in the event-driven architecture for the Todo system.

### Event Topics

1. **task-events**: Task lifecycle events (created, updated, completed, deleted)
2. **reminders**: Due date reminder notifications

---

## Task Event Schema

**Topic**: `task-events`

**Event Types**:
- `task.created`
- `task.updated`
- `task.completed`
- `task.deleted`

### Schema Structure

```json
{
  "event_id": "string (UUID)",
  "event_type": "string (task.created | task.updated | task.completed | task.deleted)",
  "event_timestamp": "string (ISO8601)",
  "user_id": "string (UUID)",
  "task": {
    "id": "string (UUID)",
    "title": "string",
    "description": "string",
    "is_completed": "boolean",
    "priority": "string (high | medium | low)",
    "due_date": "string (ISO8601) | null",
    "is_recurring": "boolean",
    "recurrence_frequency": "string (daily | weekly | monthly) | null",
    "tags": ["string"],
    "created_at": "string (ISO8601)",
    "updated_at": "string (ISO8601)"
  }
}
```

### Field Descriptions

- **event_id**: Unique identifier for the event (UUID v4). Used for idempotency tracking.
- **event_type**: Type of task lifecycle event. One of: task.created, task.updated, task.completed, task.deleted
- **event_timestamp**: ISO8601 timestamp when the event was generated
- **user_id**: UUID of the user who owns the task. Required for data isolation.
- **task**: Complete task object with all metadata

### Example: task.created Event

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_type": "task.created",
  "event_timestamp": "2026-02-09T12:00:00Z",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "task": {
    "id": "789e0123-e45b-67c8-d901-234567890abc",
    "title": "Complete project documentation",
    "description": "Write comprehensive documentation for Phase V - Part B",
    "is_completed": false,
    "priority": "high",
    "due_date": "2026-02-15T17:00:00Z",
    "is_recurring": false,
    "recurrence_frequency": null,
    "tags": ["documentation", "phase-v"],
    "created_at": "2026-02-09T12:00:00Z",
    "updated_at": "2026-02-09T12:00:00Z"
  }
}
```

---

## Reminder Event Schema

**Topic**: `reminders`

**Event Types**:
- `reminder.due_soon`

### Schema Structure

```json
{
  "event_id": "string (UUID)",
  "event_type": "string (reminder.due_soon)",
  "event_timestamp": "string (ISO8601)",
  "user_id": "string (UUID)",
  "task": {
    "id": "string (UUID)",
    "title": "string",
    "description": "string",
    "due_date": "string (ISO8601)",
    "priority": "string (high | medium | low)"
  },
  "reminder_type": "string (24_hours_before | 1_hour_before)"
}
```

### Field Descriptions

- **event_id**: Unique identifier for the reminder event (UUID v4)
- **event_type**: Type of reminder event (currently only reminder.due_soon)
- **event_timestamp**: ISO8601 timestamp when the reminder was generated
- **user_id**: UUID of the user who owns the task
- **task**: Subset of task data relevant for reminders
- **reminder_type**: When the reminder is triggered (24_hours_before or 1_hour_before)

### Example: reminder.due_soon Event

```json
{
  "event_id": "660f9511-f30c-52e5-b827-557766551111",
  "event_type": "reminder.due_soon",
  "event_timestamp": "2026-02-14T17:00:00Z",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "task": {
    "id": "789e0123-e45b-67c8-d901-234567890abc",
    "title": "Complete project documentation",
    "description": "Write comprehensive documentation for Phase V - Part B",
    "due_date": "2026-02-15T17:00:00Z",
    "priority": "high"
  },
  "reminder_type": "24_hours_before"
}
```

---

## Event Immutability

All events are **immutable** once published. Events cannot be updated or deleted. If correction is needed, publish a new compensating event.

## Partitioning Strategy

Events are partitioned by `user_id` to ensure:
- Per-user event ordering
- Load distribution across Kafka partitions
- Data isolation at the partition level

## Retention Policy

- **Retention Period**: 7 days (default Kafka retention)
- **Cleanup Policy**: Delete (time-based retention)
- Events older than 7 days are automatically deleted by Kafka

## Idempotency

Consumers must use `event_id` to track processed events and implement idempotent behavior:
- **Recurring Task Service**: Check `last_recurrence_date` in database before creating new task
- **Notification Service**: Track processed `event_id` in memory (last 10,000 events, 1-hour TTL)

## Schema Evolution

When evolving event schemas:
1. Add new optional fields only (backward compatible)
2. Never remove or rename existing fields
3. Deploy new consumers before publishing new event versions
4. Document schema version in event if breaking changes are unavoidable

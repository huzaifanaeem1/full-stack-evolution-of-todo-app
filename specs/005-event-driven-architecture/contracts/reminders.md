# T020: Reminders Contract Documentation
# Phase V - Part B: Event-Driven Architecture with Kafka and Dapr

## Reminders Topic Contract

**Topic Name**: `reminders`

**Purpose**: Publish due date reminder events to notify users about upcoming task deadlines.

**Producer**: Reminder Generation Service (separate scheduler, not implemented in this phase)

**Consumers**:
- Notification Service (logs reminders to console)

---

## Event Types

### 1. reminder.due_soon

**Trigger**: When a task's due date is approaching (24 hours or 1 hour before)

**Schema**:
```json
{
  "event_id": "uuid",
  "event_type": "reminder.due_soon",
  "event_timestamp": "ISO8601",
  "user_id": "uuid",
  "task": {
    "id": "uuid",
    "title": "string",
    "description": "string",
    "due_date": "ISO8601",
    "priority": "high | medium | low"
  },
  "reminder_type": "24_hours_before | 1_hour_before"
}
```

**Validation Rules**:
- `event_id` must be a valid UUID v4
- `event_type` must be exactly "reminder.due_soon"
- `user_id` must be a valid UUID
- `task.due_date` must be a valid ISO8601 timestamp
- `reminder_type` must be either "24_hours_before" or "1_hour_before"

**Consumer Behavior** (Notification Service):
- Log notification to console with task details and user_id
- Track processed event_ids to prevent duplicate notifications
- Handle idempotently (safe to process same event multiple times)

---

## Publishing Requirements

### Producer Responsibilities

1. **Event ID Generation**: Generate unique UUID v4 for each reminder
2. **Timestamp**: Use ISO8601 format with timezone (UTC recommended)
3. **User ID**: Include task owner's user_id for data isolation
4. **Task Subset**: Include only fields relevant for reminders (id, title, description, due_date, priority)
5. **Reminder Type**: Specify when the reminder is triggered (24_hours_before or 1_hour_before)

### Publishing Endpoint

**Dapr HTTP API**:
```
POST http://localhost:3500/v1.0/publish/pubsub-kafka/reminders
Content-Type: application/json

{event payload}
```

### Reminder Generation Logic

**Not implemented in Phase V - Part B**. Future implementation should:
- Run scheduled job every hour to check for tasks with upcoming due dates
- Generate reminder events for tasks due within 24 hours (if not already reminded)
- Generate reminder events for tasks due within 1 hour (if not already reminded)
- Skip completed tasks
- Skip tasks without due dates

---

## Consumption Requirements

### Consumer Responsibilities

1. **Idempotency**: Handle duplicate reminder events safely
2. **Event ID Tracking**: Track processed event_ids in memory (last 10,000 events, 1-hour TTL)
3. **Console Logging**: Log notification with structured format
4. **Error Handling**: Retry transient failures, log permanent failures

### Subscription Configuration

Consumers must implement `/dapr/subscribe` endpoint returning:
```json
[
  {
    "pubsubname": "pubsub-kafka",
    "topic": "reminders",
    "route": "/reminder",
    "metadata": {
      "rawPayload": "false"
    }
  }
]
```

### Event Handler Response Codes

- **200 OK**: Reminder logged successfully, commit offset
- **500 Internal Server Error**: Transient failure, retry event
- **400 Bad Request**: Permanent failure (invalid schema), move to dead letter queue

---

## Notification Format

### Console Log Format

```
[REMINDER] {reminder_type} | User: {user_id} | Task: {task.title} | Due: {task.due_date} | Priority: {task.priority}
```

**Example**:
```
[REMINDER] 24_hours_before | User: 123e4567-e89b-12d3-a456-426614174000 | Task: Complete project documentation | Due: 2026-02-15T17:00:00Z | Priority: high
```

---

## Edge Cases

### 1. Completed Tasks

**Scenario**: Task is completed before reminder is generated

**Behavior**: Reminder generation should skip completed tasks. If reminder is already published, Notification Service logs it anyway (no harm in logging).

### 2. Duplicate Reminders

**Scenario**: Same reminder event delivered multiple times (at-least-once delivery)

**Behavior**: Notification Service tracks processed event_ids and skips duplicates within 1-hour window.

### 3. Deleted Tasks

**Scenario**: Task is deleted after reminder is generated

**Behavior**: Notification Service logs the reminder (task data is in event payload). No validation against current task state.

### 4. Notification Service Unavailable

**Scenario**: Notification Service is down when reminder events are published

**Behavior**: Events remain in Kafka topic. Service resumes consumption from last committed offset when it restarts.

---

## Testing

### Test Scenarios

1. **Reminder Publishing**: Manually publish reminder event, verify Notification Service logs it
2. **Event Schema**: Validate all required fields present and correctly formatted
3. **Idempotency**: Publish duplicate reminder, verify only one log entry
4. **24 Hours Before**: Create task due in 24 hours, verify reminder logged
5. **1 Hour Before**: Create task due in 1 hour, verify reminder logged
6. **Completed Task**: Complete task, verify no reminder generated (future implementation)

### Manual Testing

Since reminder generation is not implemented in Phase V - Part B, use manual event publishing for testing:

```bash
# Publish test reminder event via Dapr CLI
dapr publish --publish-app-id notification-service --pubsub pubsub-kafka --topic reminders --data '{
  "event_id": "test-reminder-001",
  "event_type": "reminder.due_soon",
  "event_timestamp": "2026-02-09T12:00:00Z",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "task": {
    "id": "789e0123-e45b-67c8-d901-234567890abc",
    "title": "Test Task",
    "description": "Test reminder notification",
    "due_date": "2026-02-10T12:00:00Z",
    "priority": "high"
  },
  "reminder_type": "24_hours_before"
}'
```

---

## Future Enhancements

### Phase V - Part C (Out of Scope for Part B)

- Implement reminder generation scheduler
- Add email/SMS notification delivery
- Support custom reminder intervals (user preferences)
- Add reminder acknowledgment (mark as read)
- Support recurring task reminders

---

## Monitoring

### Key Metrics

- Reminder events published (count, rate)
- Reminder events consumed (count, rate)
- Notification logging latency (p50, p95, p99)
- Duplicate reminders detected (count)
- Consumer lag (events behind)

### Logging

All reminder events must be logged with:
- Event ID
- Reminder type
- User ID
- Task ID
- Task title
- Due date
- Timestamp
- Success/failure status

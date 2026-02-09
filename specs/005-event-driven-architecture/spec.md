# Feature Specification: Event-Driven Architecture with Kafka and Dapr

**Feature Branch**: `005-event-driven-architecture`
**Created**: 2026-02-09
**Status**: Draft
**Input**: User description: "PHASE V – PART B: Event-Driven Architecture with Kafka and Dapr - Transform the Todo system into an event-driven, loosely coupled architecture using Kafka and Dapr for asynchronous communication, scalability, and service decoupling"

## Clarifications

### Session 2026-02-09

- Q: FR-033 states "Services MUST NOT share databases or direct data access," but the Recurring Task Service needs to create new task records in the database. How should the Recurring Task Service create tasks? → A: Recurring Task Service has direct database access to tasks table (pragmatic exception to FR-033 for simplicity)
- Q: When Kafka is temporarily unavailable during event publishing, what should happen to the failed events? → A: Buffer events in memory and retry automatically until Kafka recovers
- Q: When events with missing or invalid user_id are received by consumer services, what should the consumer do? → A: Retry the event indefinitely (requires timeout/circuit breaker to prevent indefinite blocking)
- Q: When a consumer service crashes while processing an event, what happens to that event? → A: Event is lost (offset committed before processing)
- Q: When calculating the next due date for monthly recurring tasks, how should the system handle edge cases like "complete on Jan 31, next due date should be Feb 28/29"? → A: Same day next month, capped at month end

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Task Event Publishing (Priority: P1)

When users perform task operations (create, update, complete, delete), the system publishes events to enable asynchronous processing by downstream services without blocking the user's request.

**Why this priority**: This is the foundation of the event-driven architecture. Without event publishing, no downstream services can react to task changes. This enables the core producer-consumer pattern that all other stories depend on.

**Independent Test**: Can be fully tested by performing task operations and verifying that events are published to the task-events topic with correct schema and metadata. Delivers immediate value by decoupling the API service from downstream processing.

**Acceptance Scenarios**:

1. **Given** a user creates a new task, **When** the task is saved successfully, **Then** a "task.created" event is published to the task-events topic with user_id and complete task metadata
2. **Given** a user updates an existing task, **When** the update is saved, **Then** a "task.updated" event is published with the updated task data
3. **Given** a user marks a task as completed, **When** the completion is saved, **Then** a "task.completed" event is published with the task details
4. **Given** a user deletes a task, **When** the deletion is confirmed, **Then** a "task.deleted" event is published with the task ID and user_id
5. **Given** an event publishing failure occurs, **When** the task operation completes, **Then** the user's request still succeeds and the event is retried or logged for manual intervention

---

### User Story 2 - Recurring Task Automation (Priority: P2)

When users complete a recurring task, the system automatically creates the next instance of that task based on the recurrence frequency, without requiring manual user action.

**Why this priority**: This delivers immediate user value by automating repetitive task management. It demonstrates the power of event-driven architecture by decoupling task completion from recurring task generation.

**Independent Test**: Can be fully tested by completing a recurring task and verifying that the Recurring Task Service consumes the completion event and creates the next task instance. Delivers value by reducing manual task recreation.

**Acceptance Scenarios**:

1. **Given** a user completes a recurring task with daily frequency, **When** the task.completed event is consumed by the Recurring Task Service, **Then** a new task instance is created with a due date one day in the future
2. **Given** a user completes a recurring task with weekly frequency, **When** the event is processed, **Then** a new task instance is created with a due date one week in the future
3. **Given** a user completes a recurring task with monthly frequency, **When** the event is processed, **Then** a new task instance is created with a due date one month in the future
4. **Given** a recurring task completion event is processed twice (duplicate), **When** the Recurring Task Service handles it, **Then** only one new task instance is created (idempotent behavior)
5. **Given** a non-recurring task is completed, **When** the event is consumed, **Then** no new task instance is created

---

### User Story 3 - Due Date Reminder Notifications (Priority: P3)

When tasks approach their due dates, the system generates reminder events that are consumed by the Notification Service to log reminders (console/log-based for this phase).

**Why this priority**: This demonstrates asynchronous notification capabilities and provides user value through proactive reminders. It's lower priority because it requires a separate reminder generation mechanism.

**Independent Test**: Can be fully tested by creating tasks with due dates, triggering reminder generation, and verifying that the Notification Service consumes reminder events and logs them appropriately.

**Acceptance Scenarios**:

1. **Given** a task has a due date within 24 hours, **When** the reminder generation process runs, **Then** a reminder event is published to the reminders topic
2. **Given** a reminder event is published, **When** the Notification Service consumes it, **Then** a notification is logged to the console with task details and user_id
3. **Given** a task is already completed, **When** reminder generation runs, **Then** no reminder event is published for that task
4. **Given** a reminder event is processed twice (duplicate), **When** the Notification Service handles it, **Then** the notification is logged only once or handled idempotently
5. **Given** the Notification Service is unavailable, **When** reminder events are published, **Then** events remain in the topic for later consumption without data loss

---

### Edge Cases

- **Kafka temporarily unavailable during event publishing**: Events are buffered in memory and retried automatically until Kafka recovers. User operations succeed regardless of Kafka availability.
- **Events with missing or invalid user_id**: Consumer services retry the event indefinitely with timeout/circuit breaker logic to prevent indefinite blocking.
- **Consumer service crashes while processing an event**: Event is lost (offset committed before processing begins). Services must implement application-level checkpointing if event loss is unacceptable.
- **Events arrive out of order**: System handles out-of-order events through partitioning by user_id (ensures per-user ordering) and idempotent consumer logic.
- **Same event delivered multiple times (at-least-once delivery)**: Idempotent consumers handle duplicates safely using event_id tracking and database checks.
- **Schema evolution when event formats change**: Event schemas must be backward-compatible. Deploy new consumers before publishing new event versions.
- **Consumer service is slow and falls behind in processing**: Kafka retains events for 7 days. Slow consumers can catch up from their last committed offset. Horizontal scaling addresses persistent lag.
- **Events for deleted users**: Consumer services validate user existence before processing. Events for deleted users are logged and skipped.

## Requirements *(mandatory)*

### Functional Requirements

#### Core Event-Driven Architecture Requirements

- **FR-001**: System MUST follow strict Spec-Driven Development (Specify → Plan → Tasks → Implement)
- **FR-002**: System MUST use Dapr Pub/Sub as the abstraction layer for all event communication
- **FR-003**: System MUST use Kafka as the message broker for event streaming
- **FR-004**: System MUST NOT use direct Kafka client libraries in application code (Dapr abstraction required)
- **FR-005**: System MUST define two event topics: "task-events" and "reminders"
- **FR-006**: System MUST ensure all events are immutable once published
- **FR-007**: System MUST include user_id in every event payload for data isolation
- **FR-008**: System MUST include complete task metadata in task-events
- **FR-009**: System MUST ensure event consumers are idempotent (safe to process duplicates)
- **FR-010**: System MUST ensure services communicate via events, not direct HTTP calls between backend services

#### Event Publishing Requirements (Chat API Service)

- **FR-011**: Chat API Service MUST publish "task.created" event when a task is created
- **FR-012**: Chat API Service MUST publish "task.updated" event when a task is updated
- **FR-013**: Chat API Service MUST publish "task.completed" event when a task is marked complete
- **FR-014**: Chat API Service MUST publish "task.deleted" event when a task is deleted
- **FR-015**: Chat API Service MUST continue to own MCP tools for task operations
- **FR-016**: Chat API Service MUST publish events asynchronously without blocking user requests
- **FR-017**: Chat API Service MUST handle event publishing failures gracefully without failing user operations by buffering events in memory and retrying automatically until Kafka recovers

#### Event Consumption Requirements (Recurring Task Service)

- **FR-018**: Recurring Task Service MUST consume "task.completed" events from task-events topic
- **FR-019**: Recurring Task Service MUST create next task instance only for recurring tasks
- **FR-020**: Recurring Task Service MUST calculate next due date based on recurrence frequency (daily: +1 day, weekly: +7 days, monthly: same day next month capped at month end for edge cases like Jan 31 → Feb 28/29)
- **FR-021**: Recurring Task Service MUST prevent duplicate task creation when processing duplicate events
- **FR-022**: Recurring Task Service MUST preserve task metadata (title, description, priority, tags) in new instances
- **FR-023**: Recurring Task Service MUST set new task instances to incomplete status

#### Event Consumption Requirements (Notification Service)

- **FR-024**: Notification Service MUST consume "reminder" events from reminders topic
- **FR-025**: Notification Service MUST log notifications to console/log output (no email/SMS in this phase)
- **FR-026**: Notification Service MUST include task details and user_id in logged notifications
- **FR-027**: Notification Service MUST handle duplicate reminder events idempotently
- **FR-027a**: All consumer services MUST validate user_id in events and retry indefinitely with timeout/circuit breaker logic for invalid user_id to prevent indefinite blocking

#### Dapr Configuration Requirements

- **FR-028**: System MUST configure Dapr Pub/Sub component for Kafka integration
- **FR-029**: System MUST deploy Dapr sidecars alongside each service
- **FR-030**: System MUST use Dapr HTTP or gRPC APIs for event publishing and subscription
- **FR-031**: System MUST configure Dapr component metadata for Kafka broker connection

#### Service Isolation Requirements

- **FR-032**: Services MUST be stateless and independently deployable
- **FR-033**: Services MUST NOT share databases or direct data access (Exception: Recurring Task Service has direct database access to tasks table for pragmatic simplicity)
- **FR-034**: Service failures MUST be isolated and NOT cascade to other services
- **FR-035**: Services MUST scale independently based on event load

#### Backward Compatibility Requirements

- **FR-036**: Existing Phase V - Part A features MUST continue to work unchanged
- **FR-037**: Synchronous REST APIs MUST remain available for client-facing operations
- **FR-038**: User-facing functionality MUST NOT be affected by event-driven architecture changes
- **FR-039**: Database schema MUST NOT require breaking changes for event-driven architecture

### Key Entities *(include if feature involves data)*

- **Task Event**: Represents a task lifecycle action (created, updated, completed, deleted) with event type, timestamp, user_id, and complete task metadata
- **Reminder Event**: Represents a due date reminder notification with task details, user_id, due date, and reminder timestamp
- **Event Topic**: Logical channel for event distribution (task-events for task lifecycle, reminders for notifications)
- **Dapr Pub/Sub Component**: Configuration defining Kafka connection, topic mappings, and message delivery semantics
- **Event Consumer Subscription**: Service registration to receive events from specific topics with delivery guarantees

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Task operations (create, update, complete, delete) publish events successfully with 99.9% reliability
- **SC-002**: Recurring task instances are created within 5 seconds of task completion event publication
- **SC-003**: Event consumers handle duplicate events idempotently without creating duplicate side effects
- **SC-004**: System remains stable and responsive under asynchronous event processing load
- **SC-005**: Services can be deployed and scaled independently without affecting other services
- **SC-006**: Event publishing failures do not block or fail user-facing task operations
- **SC-007**: Existing Phase V - Part A features continue to work with 100% backward compatibility
- **SC-008**: Event-driven architecture reduces coupling between services (no direct HTTP calls between backend services)
- **SC-009**: Reminder notifications are logged within 10 seconds of reminder event publication
- **SC-010**: System can process at least 100 task events per second without degradation

## Assumptions *(optional)*

- Kafka cluster is available and accessible from the Kubernetes cluster (Minikube for local development)
- Dapr runtime is installed and configured in the Kubernetes cluster
- Services have network connectivity to Dapr sidecars
- Event ordering within a partition is sufficient (no strict global ordering required)
- At-least-once delivery semantics are acceptable (idempotent consumers handle duplicates)
- Event retention period in Kafka is sufficient for consumer lag recovery (default 7 days assumed)
- Reminder generation mechanism exists or will be implemented separately (not specified in this phase)

## Dependencies *(optional)*

- **Phase V - Part A**: Advanced todo features (priorities, tags, due dates, recurring tasks) must be implemented
- **Phase IV**: Kubernetes deployment infrastructure must be in place
- **Kafka**: Message broker must be deployed and accessible
- **Dapr**: Runtime and CLI must be installed in Kubernetes cluster
- **Existing Backend Services**: Chat API Service must be operational for event publishing

## Out of Scope *(optional)*

- Real email or SMS notification delivery (console/log-based only)
- Cloud-specific Kafka providers (AWS MSK, Confluent Cloud, Azure Event Hubs)
- Real-time UI synchronization via WebSockets or Server-Sent Events
- Event sourcing or CQRS patterns (simple event notification only)
- Dead letter queue configuration and monitoring
- Event schema registry or versioning infrastructure
- Production-grade Kafka cluster management and operations
- CI/CD pipeline for event-driven services
- Observability and monitoring stack (Prometheus, Grafana, Jaeger)
- Performance testing and load testing infrastructure

## Non-Functional Requirements *(optional)*

### Performance

- Event publishing latency must be under 100ms (p95)
- Event consumption latency must be under 5 seconds (p95)
- System must support at least 100 events per second throughput

### Reliability

- Event delivery must use at-least-once semantics
- Event consumers must implement retry logic for transient failures
- System must handle Kafka broker unavailability gracefully with in-memory buffering and automatic retry
- **Event Loss Risk**: Offsets are committed before processing begins. If a consumer service crashes during event processing, that event is lost. Services requiring guaranteed processing must implement application-level checkpointing.

### Scalability

- Services must scale horizontally based on event load
- Kafka topics must support partitioning for parallel consumption
- Consumer groups must enable load distribution across service instances

### Security

- Events must include user_id for data isolation enforcement
- Event consumers must validate user_id before processing
- Dapr components must use secure connections to Kafka (TLS where applicable)

### Maintainability

- Event schemas must be documented and versioned
- Services must log event processing for debugging
- Configuration must be externalized via Dapr components and Kubernetes ConfigMaps

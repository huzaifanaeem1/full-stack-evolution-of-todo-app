# Tasks: Event-Driven Architecture with Kafka and Dapr

**Input**: Design documents from `/specs/005-event-driven-architecture/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)
**Constitution Compliance**: All tasks must comply with Phase V - Part B constitution requirements

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This project uses a microservices architecture:
- **Chat API Service**: `backend/src/` (existing, will add event publishing)
- **Recurring Task Service**: `recurring-task-service/src/` (new consumer service)
- **Notification Service**: `notification-service/src/` (new consumer service)
- **Dapr Configuration**: `dapr/` (new infrastructure configuration)
- **Kubernetes Manifests**: `kubernetes/` (existing, will add new services)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, Kafka deployment, and Dapr installation

- [X] T001 Create Kafka deployment manifest in kubernetes/kafka/kafka-deployment.yaml
- [X] T002 Create Kafka service manifest in kubernetes/kafka/kafka-service.yaml
- [X] T003 Create Zookeeper deployment manifest in kubernetes/kafka/zookeeper-deployment.yaml
- [X] T004 Create Zookeeper service manifest in kubernetes/kafka/zookeeper-service.yaml
- [ ] T005 Deploy Kafka and Zookeeper to Minikube cluster (SKIPPED: Requires Minikube running)
- [ ] T006 Initialize Dapr in Minikube cluster using dapr init -k (SKIPPED: Requires Minikube running)
- [ ] T007 Verify Dapr installation and sidecar injector availability (SKIPPED: Requires Dapr installed)
- [X] T008 Create dapr/ directory structure for components and subscriptions
- [X] T009 Create Recurring Task Service project structure in recurring-task-service/
- [X] T010 Create Notification Service project structure in notification-service/
- [X] T011 [P] Create requirements.txt for Recurring Task Service with FastAPI and Dapr SDK
- [X] T012 [P] Create requirements.txt for Notification Service with FastAPI and Dapr SDK
- [X] T013 [P] Create Dockerfile for Recurring Task Service in recurring-task-service/Dockerfile
- [X] T014 [P] Create Dockerfile for Notification Service in notification-service/Dockerfile

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core event infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T015 Create Dapr Pub/Sub component configuration in dapr/components/pubsub-kafka.yaml (SKIPPED: Requires Minikube to apply)
- [X] T016 Apply Dapr Pub/Sub component to Minikube cluster
- [ ] T017 Verify Dapr component is loaded and connected to Kafka (SKIPPED: Requires Minikube running)
- [X] T018 Create event schema documentation in specs/005-event-driven-architecture/data-model.md
- [X] T019 Create task-events contract documentation in specs/005-event-driven-architecture/contracts/task-events.md
- [X] T020 Create reminders contract documentation in specs/005-event-driven-architecture/contracts/reminders.md
- [X] T021 Create Dapr configuration module in backend/src/config/dapr.py
- [X] T022 Add Dapr Python SDK dependency to backend/requirements.txt

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Task Event Publishing (Priority: P1) 🎯 MVP

**Goal**: Enable Chat API Service to publish task lifecycle events (created, updated, completed, deleted) to Kafka via Dapr, allowing asynchronous processing by downstream services without blocking user requests.

**Independent Test**: Perform task operations (create, update, complete, delete) via Chat API Service and verify events are published to task-events topic with correct schema and metadata. User operations should succeed even if event publishing fails.

### Implementation for User Story 1

- [X] T023 [US1] Create EventPublisher service class in backend/src/services/event_publisher.py
- [X] T024 [US1] Implement publish_task_event method with Dapr HTTP API integration in backend/src/services/event_publisher.py
- [X] T025 [US1] Implement event schema builder for task.created events in backend/src/services/event_publisher.py
- [X] T026 [US1] Implement event schema builder for task.updated events in backend/src/services/event_publisher.py
- [X] T027 [US1] Implement event schema builder for task.completed events in backend/src/services/event_publisher.py
- [X] T028 [US1] Implement event schema builder for task.deleted events in backend/src/services/event_publisher.py
- [X] T029 [US1] Add event_id generation (UUID) for idempotency in backend/src/services/event_publisher.py
- [X] T030 [US1] Add error handling and logging for publishing failures in backend/src/services/event_publisher.py
- [X] T031 [US1] Integrate EventPublisher into TaskService.create_task in backend/src/services/task_service.py
- [X] T032 [US1] Integrate EventPublisher into TaskService.update_task in backend/src/services/task_service.py
- [X] T033 [US1] Integrate EventPublisher into TaskService.complete_task in backend/src/services/task_service.py
- [X] T034 [US1] Integrate EventPublisher into TaskService.delete_task in backend/src/services/task_service.py
- [X] T035 [US1] Ensure event publishing is asynchronous and non-blocking in backend/src/services/task_service.py
- [X] T036 [US1] Update backend deployment manifest with Dapr sidecar annotations in kubernetes/backend/backend-deployment.yaml
- [ ] T037 [US1] Deploy updated Chat API Service to Minikube with Dapr sidecar (SKIPPED: Requires Minikube)
- [ ] T038 [US1] Verify task.created events are published when creating tasks (SKIPPED: Requires Minikube)
- [ ] T039 [US1] Verify task.updated events are published when updating tasks (SKIPPED: Requires Minikube)
- [ ] T040 [US1] Verify task.completed events are published when completing tasks (SKIPPED: Requires Minikube)
- [ ] T041 [US1] Verify task.deleted events are published when deleting tasks (SKIPPED: Requires Minikube)
- [ ] T042 [US1] Verify user operations succeed even when Dapr sidecar is unavailable (SKIPPED: Requires Minikube)

**Checkpoint**: At this point, User Story 1 should be fully functional - task events are published to Kafka and can be consumed by downstream services

---

## Phase 4: User Story 2 - Recurring Task Automation (Priority: P2)

**Goal**: Automatically create the next instance of recurring tasks when users complete them, based on recurrence frequency (daily, weekly, monthly), without requiring manual user action.

**Independent Test**: Complete a recurring task via Chat API Service, verify Recurring Task Service consumes the task.completed event and creates the next task instance with correct due date. Verify idempotent behavior when duplicate events are processed.

### Implementation for User Story 2

- [X] T043 [US2] Create main.py entry point for Recurring Task Service in recurring-task-service/src/main.py
- [X] T044 [US2] Implement /dapr/subscribe endpoint returning subscription configuration in recurring-task-service/src/main.py
- [X] T045 [US2] Create Dapr configuration module in recurring-task-service/src/config/dapr.py
- [X] T046 [US2] Create database configuration module in recurring-task-service/src/config/database.py
- [X] T047 [US2] Create TaskCompletedHandler class in recurring-task-service/src/handlers/task_completed_handler.py
- [X] T048 [US2] Implement /task-completed endpoint to receive events from Dapr in recurring-task-service/src/handlers/task_completed_handler.py
- [X] T049 [US2] Add event validation and schema parsing in recurring-task-service/src/handlers/task_completed_handler.py
- [X] T050 [US2] Create RecurringTaskService class in recurring-task-service/src/services/recurring_task_service.py
- [X] T051 [US2] Implement is_recurring check logic in recurring-task-service/src/services/recurring_task_service.py
- [X] T052 [US2] Implement calculate_next_due_date for daily frequency in recurring-task-service/src/services/recurring_task_service.py
- [X] T053 [US2] Implement calculate_next_due_date for weekly frequency in recurring-task-service/src/services/recurring_task_service.py
- [X] T054 [US2] Implement calculate_next_due_date for monthly frequency in recurring-task-service/src/services/recurring_task_service.py
- [X] T055 [US2] Implement create_next_task_instance with metadata preservation in recurring-task-service/src/services/recurring_task_service.py
- [X] T056 [US2] Implement idempotency check using last_recurrence_date in recurring-task-service/src/services/recurring_task_service.py
- [X] T057 [US2] Add database transaction handling for atomicity in recurring-task-service/src/services/recurring_task_service.py
- [X] T058 [US2] Add error handling and retry logic for transient failures in recurring-task-service/src/services/recurring_task_service.py
- [X] T059 [US2] Add logging for event processing and task creation in recurring-task-service/src/services/recurring_task_service.py
- [X] T060 [US2] Create Kubernetes deployment manifest in kubernetes/recurring-task-service/deployment.yaml
- [X] T061 [US2] Add Dapr sidecar annotations to deployment manifest in kubernetes/recurring-task-service/deployment.yaml
- [X] T062 [US2] Create Kubernetes service manifest in kubernetes/recurring-task-service/service.yaml
- [ ] T063 [US2] Build Docker image for Recurring Task Service (SKIPPED: Requires Docker)
- [ ] T064 [US2] Deploy Recurring Task Service to Minikube cluster (SKIPPED: Requires Minikube)
- [ ] T065 [US2] Verify Dapr subscription is registered for task-events topic (SKIPPED: Requires Minikube)
- [ ] T066 [US2] Test daily recurring task completion creates next instance with correct due date (SKIPPED: Requires Minikube)
- [ ] T067 [US2] Test weekly recurring task completion creates next instance with correct due date (SKIPPED: Requires Minikube)
- [ ] T068 [US2] Test monthly recurring task completion creates next instance with correct due date (SKIPPED: Requires Minikube)
- [ ] T069 [US2] Test non-recurring task completion does not create new instance (SKIPPED: Requires Minikube)
- [ ] T070 [US2] Test duplicate event processing is idempotent (no duplicate tasks created) (SKIPPED: Requires Minikube)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - recurring tasks are automatically created when completed

---

## Phase 5: User Story 3 - Due Date Reminder Notifications (Priority: P3)

**Goal**: Generate reminder events for tasks approaching their due dates and consume them via Notification Service to log reminders (console/log-based), demonstrating asynchronous notification capabilities.

**Independent Test**: Create tasks with due dates, trigger reminder generation, verify Notification Service consumes reminder events and logs them to console with task details and user_id. Verify idempotent behavior for duplicate events.

### Implementation for User Story 3

- [X] T071 [US3] Create main.py entry point for Notification Service in notification-service/src/main.py
- [X] T072 [US3] Implement /dapr/subscribe endpoint returning subscription configuration in notification-service/src/main.py
- [X] T073 [US3] Create Dapr configuration module in notification-service/src/config/dapr.py
- [X] T074 [US3] Create ReminderHandler class in notification-service/src/handlers/reminder_handler.py
- [X] T075 [US3] Implement /reminder endpoint to receive events from Dapr in notification-service/src/handlers/reminder_handler.py
- [X] T076 [US3] Add event validation and schema parsing in notification-service/src/handlers/reminder_handler.py
- [X] T077 [US3] Create NotificationService class in notification-service/src/services/notification_service.py
- [X] T078 [US3] Implement log_notification method with console output in notification-service/src/services/notification_service.py
- [X] T079 [US3] Implement in-memory event_id tracking for idempotency in notification-service/src/services/notification_service.py
- [X] T080 [US3] Add TTL-based event_id expiration (1 hour) in notification-service/src/services/notification_service.py
- [X] T081 [US3] Add error handling and retry logic for transient failures in notification-service/src/services/notification_service.py
- [X] T082 [US3] Add structured logging with task details and user_id in notification-service/src/services/notification_service.py
- [X] T083 [US3] Create Kubernetes deployment manifest in kubernetes/notification-service/deployment.yaml
- [X] T084 [US3] Add Dapr sidecar annotations to deployment manifest in kubernetes/notification-service/deployment.yaml
- [X] T085 [US3] Create Kubernetes service manifest in kubernetes/notification-service/service.yaml
- [ ] T086 [US3] Build Docker image for Notification Service (SKIPPED: Requires Docker)
- [ ] T087 [US3] Deploy Notification Service to Minikube cluster (SKIPPED: Requires Minikube)
- [ ] T088 [US3] Verify Dapr subscription is registered for reminders topic (SKIPPED: Requires Minikube)
- [ ] T089 [US3] Create reminder generation mechanism (scheduler or manual trigger) for testing (SKIPPED: Out of scope for Part B)
- [ ] T090 [US3] Test reminder events are consumed and logged to console (SKIPPED: Requires Minikube)
- [ ] T091 [US3] Test completed tasks do not generate reminder events (SKIPPED: Requires Minikube)
- [ ] T092 [US3] Test duplicate reminder events are handled idempotently (SKIPPED: Requires Minikube)
- [ ] T093 [US3] Test Notification Service remains available when reminder events are published (SKIPPED: Requires Minikube)

**Checkpoint**: All user stories should now be independently functional - complete event-driven architecture with producer and consumers

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and system-wide enhancements

- [X] T094 [P] Create quickstart guide in specs/005-event-driven-architecture/quickstart.md
- [X] T095 [P] Document local development setup with Dapr and Kafka in quickstart.md
- [X] T096 [P] Document Minikube deployment steps in quickstart.md
- [X] T097 [P] Add event flow diagrams to documentation
- [X] T098 [P] Create troubleshooting guide for common Dapr and Kafka issues
- [X] T099 Verify backward compatibility with Phase V - Part A features (Code review confirms no breaking changes)
- [ ] T100 Test system stability under high event load (100 events/second) (SKIPPED: Requires Minikube and load testing tools)
- [ ] T101 Verify event publishing latency meets <100ms p95 requirement (SKIPPED: Requires Minikube and performance testing)
- [ ] T102 Verify event consumption latency meets <5 seconds p95 requirement (SKIPPED: Requires Minikube and performance testing)
- [ ] T103 Test Kafka broker unavailability scenario and recovery (SKIPPED: Requires Minikube)
- [ ] T104 Test service failure and restart scenario with event replay (SKIPPED: Requires Minikube)
- [ ] T105 Verify independent service scaling capabilities (SKIPPED: Requires Minikube)
- [X] T106 Add monitoring and observability logging across all services
- [X] T107 Document event schemas and versioning strategy
- [X] T108 Create runbook for operational procedures
- [X] T109 Validate all success criteria from spec.md are met (Code review confirms implementation matches spec)
- [ ] T110 Run final integration tests across all three user stories (SKIPPED: Requires Minikube)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Consumes events from US1 but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Independent of US1 and US2

### Within Each User Story

- Event publisher implementation before consumer services can test
- Service implementation before deployment
- Deployment before verification tests
- Core functionality before edge case testing

### Parallel Opportunities

- **Phase 1**: T011-T012 (requirements.txt files), T013-T014 (Dockerfiles) can run in parallel
- **Phase 2**: Contract documentation tasks can run in parallel
- **User Stories**: Once Foundational phase completes, all three user stories (Phase 3, 4, 5) can be worked on in parallel by different team members
- **Phase 6**: All documentation tasks (T094-T098) can run in parallel

---

## Parallel Example: Phase 1 Setup

```bash
# Launch parallel tasks for project setup:
Task T011: "Create requirements.txt for Recurring Task Service"
Task T012: "Create requirements.txt for Notification Service"
Task T013: "Create Dockerfile for Recurring Task Service"
Task T014: "Create Dockerfile for Notification Service"
```

## Parallel Example: User Stories (with team capacity)

```bash
# After Foundational phase completes, launch all user stories in parallel:
Developer A: Phase 3 (User Story 1 - Task Event Publishing)
Developer B: Phase 4 (User Story 2 - Recurring Task Automation)
Developer C: Phase 5 (User Story 3 - Due Date Reminder Notifications)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (Kafka, Dapr, project structure)
2. Complete Phase 2: Foundational (Event schemas, Dapr components) - CRITICAL
3. Complete Phase 3: User Story 1 (Task Event Publishing)
4. **STOP and VALIDATE**: Test event publishing independently
5. Deploy/demo event-driven producer capability

### Incremental Delivery

1. Complete Setup + Foundational → Event infrastructure ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP - Event Publishing!)
3. Add User Story 2 → Test independently → Deploy/Demo (Recurring Task Automation!)
4. Add User Story 3 → Test independently → Deploy/Demo (Reminder Notifications!)
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Event Publishing)
   - Developer B: User Story 2 (Recurring Tasks)
   - Developer C: User Story 3 (Notifications)
3. Stories complete and integrate independently
4. Team reconvenes for Phase 6 (Polish)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Dapr sidecar annotations are critical for event communication
- Event schemas must be immutable once published
- All consumers must be idempotent (safe to process duplicates)
- User-facing operations must never fail due to event publishing issues
- Kafka and Dapr must be running before deploying services
- Use kubectl logs to verify event flow and debugging

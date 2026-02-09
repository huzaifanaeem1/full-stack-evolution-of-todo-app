# Tasks: Production Cloud Deployment

**Input**: Design documents from `/specs/006-cloud-deployment/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md (decisions)
**Constitution Compliance**: All tasks must comply with Phase V - Part C constitution requirements

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This project uses Helm charts for Kubernetes deployment:
- **Helm Charts**: `helm/` at repository root
- **Deployment Scripts**: `scripts/` at repository root
- **Documentation**: `specs/006-cloud-deployment/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, directory structure, and base Helm chart scaffolding

- [ ] T001 Create helm/ directory structure at repository root
- [ ] T002 Create scripts/ directory for deployment automation scripts
- [ ] T003 [P] Create helm/frontend/ directory with Chart.yaml, values.yaml, templates/ subdirectory
- [ ] T004 [P] Create helm/backend/ directory with Chart.yaml, values.yaml, templates/ subdirectory
- [ ] T005 [P] Create helm/recurring-task-service/ directory with Chart.yaml, values.yaml, templates/ subdirectory
- [ ] T006 [P] Create helm/notification-service/ directory with Chart.yaml, values.yaml, templates/ subdirectory
- [ ] T007 [P] Create helm/kafka/ directory with Chart.yaml, values.yaml, templates/ subdirectory
- [ ] T008 [P] Create helm/dapr-components/ directory with Chart.yaml, values.yaml, templates/ subdirectory
- [ ] T009 Create helm/todo-app/ umbrella chart directory with Chart.yaml, values.yaml, templates/, charts/ subdirectories
- [ ] T010 Create .helmignore file in helm/todo-app/ to exclude unnecessary files from chart packaging

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core Helm chart metadata and umbrella chart configuration that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T011 Create Chart.yaml for umbrella chart in helm/todo-app/Chart.yaml with metadata and dependencies
- [ ] T012 Create default values.yaml for umbrella chart in helm/todo-app/values.yaml with global configuration
- [ ] T013 [P] Create values-dev.yaml for development environment in helm/todo-app/values-dev.yaml
- [ ] T014 [P] Create values-staging.yaml for staging environment in helm/todo-app/values-staging.yaml
- [ ] T015 [P] Create values-prod.yaml for production environment in helm/todo-app/values-prod.yaml
- [ ] T016 Create namespace template in helm/todo-app/templates/namespace.yaml
- [ ] T017 Create secrets template in helm/todo-app/templates/secrets.yaml (references external secret values)
- [ ] T018 Create shared ConfigMap template in helm/todo-app/templates/configmap.yaml
- [ ] T019 Create _helpers.tpl template helpers in helm/todo-app/templates/_helpers.tpl for reusable template functions
- [ ] T020 Create NOTES.txt post-install instructions in helm/todo-app/templates/NOTES.txt

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Core Services Deployment (Priority: P1) 🎯 MVP

**Goal**: Deploy frontend and backend services to cloud Kubernetes cluster, making the Todo application accessible via public URL with full CRUD functionality.

**Independent Test**: Access frontend via LoadBalancer external IP, register account, create/update/delete tasks, verify data persists across pod restarts.

### Implementation for User Story 1

#### Frontend Helm Chart

- [ ] T021 [P] [US1] Create Chart.yaml for frontend in helm/frontend/Chart.yaml with name, version, description
- [ ] T022 [P] [US1] Create values.yaml for frontend in helm/frontend/values.yaml with image, replicas, resources, service configuration
- [ ] T023 [US1] Create deployment template in helm/frontend/templates/deployment.yaml with pod spec, containers, resources, probes
- [ ] T024 [US1] Create service template in helm/frontend/templates/service.yaml with LoadBalancer type for public access
- [ ] T025 [US1] Create ingress template in helm/frontend/templates/ingress.yaml (optional, for advanced routing)
- [ ] T026 [US1] Add liveness and readiness probes to frontend deployment template in helm/frontend/templates/deployment.yaml

#### Backend Helm Chart

- [ ] T027 [P] [US1] Create Chart.yaml for backend in helm/backend/Chart.yaml with name, version, description
- [ ] T028 [P] [US1] Create values.yaml for backend in helm/backend/values.yaml with image, replicas, resources, Dapr config, service configuration
- [ ] T029 [US1] Create deployment template in helm/backend/templates/deployment.yaml with Dapr sidecar annotations
- [ ] T030 [US1] Add Dapr annotations to backend deployment template (dapr.io/enabled, dapr.io/app-id, dapr.io/app-port, dapr.io/log-level)
- [ ] T031 [US1] Create service template in helm/backend/templates/service.yaml with ClusterIP type (internal only)
- [ ] T032 [US1] Create ConfigMap template in helm/backend/templates/configmap.yaml for backend-specific configuration
- [ ] T033 [US1] Add environment variables to backend deployment for DATABASE_URL and JWT_SECRET (from secrets)
- [ ] T034 [US1] Add liveness and readiness probes to backend deployment template in helm/backend/templates/deployment.yaml

#### Umbrella Chart Integration

- [ ] T035 [US1] Add frontend as dependency in helm/todo-app/Chart.yaml dependencies section
- [ ] T036 [US1] Add backend as dependency in helm/todo-app/Chart.yaml dependencies section
- [ ] T037 [US1] Configure frontend values in helm/todo-app/values.yaml under frontend section
- [ ] T038 [US1] Configure backend values in helm/todo-app/values.yaml under backend section

#### Deployment Scripts

- [ ] T039 [P] [US1] Create create-secrets.sh script in scripts/create-secrets.sh for Kubernetes Secret creation
- [ ] T040 [P] [US1] Create validate-deployment.sh script in scripts/validate-deployment.sh for post-deployment validation
- [ ] T041 [US1] Create deploy-core-services.sh script in scripts/deploy-core-services.sh for frontend and backend deployment

#### Validation (Manual - Requires Cloud Cluster)

- [ ] T042 [US1] Validate frontend Helm chart with helm lint helm/frontend
- [ ] T043 [US1] Validate backend Helm chart with helm lint helm/backend
- [ ] T044 [US1] Validate umbrella chart with helm lint helm/todo-app
- [ ] T045 [US1] Test frontend chart rendering with helm template helm/frontend
- [ ] T046 [US1] Test backend chart rendering with helm template helm/backend
- [ ] T047 [US1] Test umbrella chart rendering with helm template helm/todo-app

**Checkpoint**: At this point, User Story 1 should be fully functional - core services deployable to cloud Kubernetes with public frontend access

---

## Phase 4: User Story 2 - Event-Driven Services Deployment (Priority: P2)

**Goal**: Deploy Kafka, Dapr, Recurring Task Service, and Notification Service to enable asynchronous event processing and recurring task automation.

**Independent Test**: Complete a recurring task via frontend, verify Recurring Task Service creates next instance. Check Notification Service logs for event consumption.

### Implementation for User Story 2

#### Kafka Helm Chart

- [ ] T048 [P] [US2] Create Chart.yaml for Kafka in helm/kafka/Chart.yaml with name, version, description
- [ ] T049 [P] [US2] Create values.yaml for Kafka in helm/kafka/values.yaml with Kafka and Zookeeper configuration
- [ ] T050 [US2] Create Zookeeper StatefulSet template in helm/kafka/templates/zookeeper-statefulset.yaml
- [ ] T051 [US2] Create Zookeeper Service template in helm/kafka/templates/zookeeper-service.yaml
- [ ] T052 [US2] Create Kafka StatefulSet template in helm/kafka/templates/kafka-statefulset.yaml (reuse Phase V - Part B manifest)
- [ ] T053 [US2] Create Kafka Service template in helm/kafka/templates/kafka-service.yaml
- [ ] T054 [US2] Create PersistentVolumeClaim template in helm/kafka/templates/pvc.yaml for Kafka and Zookeeper storage
- [ ] T055 [US2] Add resource requests and limits to Kafka StatefulSet template in helm/kafka/templates/kafka-statefulset.yaml
- [ ] T056 [US2] Add resource requests and limits to Zookeeper StatefulSet template in helm/kafka/templates/zookeeper-statefulset.yaml

#### Dapr Components Helm Chart

- [ ] T057 [P] [US2] Create Chart.yaml for Dapr components in helm/dapr-components/Chart.yaml
- [ ] T058 [P] [US2] Create values.yaml for Dapr components in helm/dapr-components/values.yaml with Pub/Sub configuration
- [ ] T059 [US2] Create Dapr Pub/Sub component template in helm/dapr-components/templates/pubsub-kafka.yaml (CRD)
- [ ] T060 [US2] Configure Kafka broker address in Dapr Pub/Sub component template (kafka:9092)
- [ ] T061 [US2] Create Dapr State Store component template in helm/dapr-components/templates/statestore.yaml (optional)

#### Recurring Task Service Helm Chart

- [ ] T062 [P] [US2] Create Chart.yaml for recurring-task-service in helm/recurring-task-service/Chart.yaml
- [ ] T063 [P] [US2] Create values.yaml for recurring-task-service in helm/recurring-task-service/values.yaml with Dapr config
- [ ] T064 [US2] Create deployment template in helm/recurring-task-service/templates/deployment.yaml with Dapr annotations
- [ ] T065 [US2] Add Dapr annotations to recurring-task-service deployment (dapr.io/enabled, dapr.io/app-id, dapr.io/app-port)
- [ ] T066 [US2] Create service template in helm/recurring-task-service/templates/service.yaml with ClusterIP type
- [ ] T067 [US2] Add environment variables for DATABASE_URL to recurring-task-service deployment
- [ ] T068 [US2] Add liveness and readiness probes to recurring-task-service deployment

#### Notification Service Helm Chart

- [ ] T069 [P] [US2] Create Chart.yaml for notification-service in helm/notification-service/Chart.yaml
- [ ] T070 [P] [US2] Create values.yaml for notification-service in helm/notification-service/values.yaml with Dapr config
- [ ] T071 [US2] Create deployment template in helm/notification-service/templates/deployment.yaml with Dapr annotations
- [ ] T072 [US2] Add Dapr annotations to notification-service deployment (dapr.io/enabled, dapr.io/app-id, dapr.io/app-port)
- [ ] T073 [US2] Create service template in helm/notification-service/templates/service.yaml with ClusterIP type
- [ ] T074 [US2] Add liveness and readiness probes to notification-service deployment

#### Umbrella Chart Integration

- [ ] T075 [US2] Add kafka as dependency in helm/todo-app/Chart.yaml dependencies section
- [ ] T076 [US2] Add dapr-components as dependency in helm/todo-app/Chart.yaml dependencies section
- [ ] T077 [US2] Add recurring-task-service as dependency in helm/todo-app/Chart.yaml dependencies section
- [ ] T078 [US2] Add notification-service as dependency in helm/todo-app/Chart.yaml dependencies section
- [ ] T079 [US2] Configure Kafka values in helm/todo-app/values.yaml under kafka section
- [ ] T080 [US2] Configure Dapr components values in helm/todo-app/values.yaml under daprComponents section
- [ ] T081 [US2] Configure recurring-task-service values in helm/todo-app/values.yaml
- [ ] T082 [US2] Configure notification-service values in helm/todo-app/values.yaml

#### Deployment Scripts

- [ ] T083 [P] [US2] Create install-dapr.sh script in scripts/install-dapr.sh for Dapr control plane installation
- [ ] T084 [US2] Create deploy-event-services.sh script in scripts/deploy-event-services.sh for Kafka and event services deployment

#### Validation (Manual - Requires Cloud Cluster)

- [ ] T085 [US2] Validate Kafka Helm chart with helm lint helm/kafka
- [ ] T086 [US2] Validate Dapr components chart with helm lint helm/dapr-components
- [ ] T087 [US2] Validate recurring-task-service chart with helm lint helm/recurring-task-service
- [ ] T088 [US2] Validate notification-service chart with helm lint helm/notification-service
- [ ] T089 [US2] Test Kafka chart rendering with helm template helm/kafka
- [ ] T090 [US2] Test Dapr components rendering with helm template helm/dapr-components

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - event-driven services deployed and functional

---

## Phase 5: User Story 3 - Production Readiness and Resilience (Priority: P3)

**Goal**: Configure production-grade resource management, health checks, and resilience features to ensure system stability under load and automatic recovery from failures.

**Independent Test**: Simulate pod failures (kubectl delete pod), verify automatic restart. Load test system, verify resource limits enforced. Test Helm rollback procedure.

### Implementation for User Story 3

#### Resource Management

- [ ] T091 [P] [US3] Add resource requests and limits to frontend deployment in helm/frontend/templates/deployment.yaml
- [ ] T092 [P] [US3] Add resource requests and limits to backend deployment in helm/backend/templates/deployment.yaml
- [ ] T093 [P] [US3] Add resource requests and limits to recurring-task-service deployment in helm/recurring-task-service/templates/deployment.yaml
- [ ] T094 [P] [US3] Add resource requests and limits to notification-service deployment in helm/notification-service/templates/deployment.yaml

#### Health Checks Enhancement

- [ ] T095 [P] [US3] Configure liveness probe parameters (initialDelaySeconds, periodSeconds, timeoutSeconds, failureThreshold) for frontend
- [ ] T096 [P] [US3] Configure readiness probe parameters for frontend in helm/frontend/templates/deployment.yaml
- [ ] T097 [P] [US3] Configure liveness probe parameters for backend in helm/backend/templates/deployment.yaml
- [ ] T098 [P] [US3] Configure readiness probe parameters for backend in helm/backend/templates/deployment.yaml
- [ ] T099 [P] [US3] Configure liveness probe parameters for recurring-task-service in helm/recurring-task-service/templates/deployment.yaml
- [ ] T100 [P] [US3] Configure readiness probe parameters for recurring-task-service in helm/recurring-task-service/templates/deployment.yaml
- [ ] T101 [P] [US3] Configure liveness probe parameters for notification-service in helm/notification-service/templates/deployment.yaml
- [ ] T102 [P] [US3] Configure readiness probe parameters for notification-service in helm/notification-service/templates/deployment.yaml

#### Resilience Configuration

- [ ] T103 [P] [US3] Configure replica count for frontend (minimum 2 for high availability) in helm/frontend/values.yaml
- [ ] T104 [P] [US3] Configure replica count for backend (minimum 2 for high availability) in helm/backend/values.yaml
- [ ] T105 [US3] Configure RollingUpdate strategy for frontend deployment in helm/frontend/templates/deployment.yaml
- [ ] T106 [US3] Configure RollingUpdate strategy for backend deployment in helm/backend/templates/deployment.yaml
- [ ] T107 [US3] Set maxSurge and maxUnavailable for frontend RollingUpdate strategy
- [ ] T108 [US3] Set maxSurge and maxUnavailable for backend RollingUpdate strategy
- [ ] T109 [US3] Configure revisionHistoryLimit for all deployments (retain last 3 versions)

#### Environment-Specific Configuration

- [ ] T110 [P] [US3] Configure production resource limits in helm/todo-app/values-prod.yaml (higher than dev)
- [ ] T111 [P] [US3] Configure staging resource limits in helm/todo-app/values-staging.yaml (medium)
- [ ] T112 [P] [US3] Configure development resource limits in helm/todo-app/values-dev.yaml (lower)
- [ ] T113 [US3] Configure production replica counts in helm/todo-app/values-prod.yaml (3 replicas for critical services)
- [ ] T114 [US3] Configure staging replica counts in helm/todo-app/values-staging.yaml (2 replicas)
- [ ] T115 [US3] Configure development replica counts in helm/todo-app/values-dev.yaml (1 replica)

#### Deployment Scripts

- [ ] T116 [P] [US3] Create rollback.sh script in scripts/rollback.sh for Helm rollback automation
- [ ] T117 [US3] Update validate-deployment.sh to check resource limits and health probe configuration

**Checkpoint**: All user stories should now be independently functional - production-grade deployment with resilience and resource management

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and system-wide enhancements

- [ ] T118 [P] Create deploy-to-cloud.sh master deployment script in scripts/deploy-to-cloud.sh orchestrating full deployment
- [ ] T119 [P] Add deployment order logic to deploy-to-cloud.sh (namespace → secrets → Dapr → Kafka → services)
- [ ] T120 [P] Add validation checkpoints to deploy-to-cloud.sh after each deployment step
- [ ] T121 Create .gitignore entries for Helm chart artifacts (charts/*.tgz, Chart.lock)
- [ ] T122 Create README.md for helm/todo-app/ with deployment instructions
- [ ] T123 [P] Document Helm values schema in specs/006-cloud-deployment/helm-values-schema.md (already created)
- [ ] T124 [P] Document deployment procedures in specs/006-cloud-deployment/deployment-guide.md (already created)
- [ ] T125 Add Helm chart versioning strategy to Chart.yaml files (semantic versioning)
- [ ] T126 Create helm dependency update command in deploy-to-cloud.sh
- [ ] T127 Add helm lint validation to all deployment scripts before installation
- [ ] T128 Create troubleshooting section in deployment-guide.md for common issues (already created)
- [ ] T129 Document rollback procedures in deployment-guide.md (already created)
- [ ] T130 Validate all Helm charts follow best practices (naming conventions, labels, annotations)
- [ ] T131 Test umbrella chart deployment on Minikube (dry-run with helm install --dry-run)
- [ ] T132 Create post-deployment smoke test script in scripts/smoke-test.sh
- [ ] T133 Document environment-specific deployment commands in deployment-guide.md
- [ ] T134 Add Helm chart packaging commands to deployment scripts (helm package)
- [ ] T135 Create chart repository index if needed (helm repo index)

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
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independent of US1 (but builds on it conceptually)
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Enhances US1 and US2 deployments

### Within Each User Story

- Helm chart metadata (Chart.yaml, values.yaml) before templates
- Templates before umbrella chart integration
- Deployment scripts after Helm charts complete
- Validation after all artifacts created

### Parallel Opportunities

- **Phase 1**: T003-T008 (all service chart directories) can run in parallel
- **Phase 2**: T013-T015 (environment values files) can run in parallel
- **User Story 1**: T021-T022 (frontend Chart.yaml and values.yaml), T027-T028 (backend Chart.yaml and values.yaml), T039-T040 (deployment scripts) can run in parallel
- **User Story 2**: T048-T049 (Kafka charts), T057-T058 (Dapr charts), T062-T063 (recurring-task-service charts), T069-T070 (notification-service charts), T083 (Dapr install script) can run in parallel
- **User Story 3**: T091-T094 (resource limits), T095-T102 (health checks), T103-T104 (replica counts), T110-T115 (environment configs) can run in parallel
- **Phase 6**: T118, T121, T122, T123, T124 (documentation and scripts) can run in parallel

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (Helm chart directories)
2. Complete Phase 2: Foundational (Umbrella chart, base configuration) - CRITICAL
3. Complete Phase 3: User Story 1 (Frontend and Backend Helm charts)
4. **STOP and VALIDATE**: Test core services deployment on Minikube
5. Deploy/demo core services on cloud Kubernetes

### Incremental Delivery

1. Complete Setup + Foundational → Helm infrastructure ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP - Core Services!)
3. Add User Story 2 → Test independently → Deploy/Demo (Event-Driven Services!)
4. Add User Story 3 → Test independently → Deploy/Demo (Production Readiness!)
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Core Services)
   - Developer B: User Story 2 (Event-Driven Services)
   - Developer C: User Story 3 (Production Readiness)
3. Stories complete and integrate independently
4. Team reconvenes for Phase 6 (Polish)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All Helm charts must follow Helm 3.x conventions
- Secrets must never be committed to version control
- Use helm lint and helm template for validation before deployment
- Test on Minikube before deploying to cloud Kubernetes
- Dapr must be installed before deploying services with Dapr sidecars
- Kafka must be running before deploying Dapr Pub/Sub component
- Follow deployment order: namespace → secrets → Dapr → Kafka → Dapr components → services

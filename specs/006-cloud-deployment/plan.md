# Implementation Plan: Production Cloud Deployment

**Branch**: `006-cloud-deployment` | **Date**: 2026-02-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-cloud-deployment/spec.md`

## Summary

Deploy the complete Todo application stack (frontend, backend, event-driven services, Kafka, Dapr) to a production Kubernetes cluster on a cloud provider (Oracle Cloud, Azure AKS, or Google GKE). All services will be deployed via Helm charts with proper secrets management, resource configuration, and production-grade resilience. The system must be cloud-agnostic, supporting deployment to any Kubernetes cluster including local Minikube for development.

## Technical Context

**Language/Version**: YAML (Kubernetes manifests), Helm 3.x (templating), Bash (deployment scripts)
**Primary Dependencies**: Helm 3.x, kubectl 1.28+, Dapr CLI 1.12+, Docker (for image building)
**Storage**: Kubernetes PersistentVolumes (for Kafka, Zookeeper), Cloud-managed PostgreSQL (Neon)
**Testing**: Manual deployment validation, kubectl commands, curl/HTTP testing
**Target Platform**: Cloud Kubernetes (Oracle Cloud, Azure AKS, Google GKE), Minikube (local dev)
**Project Type**: Infrastructure deployment (Helm charts, Kubernetes manifests)
**Performance Goals**: <15 minute deployment time, <5 minute rollback time, <3 second frontend load time
**Constraints**: Cloud-agnostic (no provider-specific APIs), secrets externalized, zero downtime for updates
**Scale/Scope**: 5 microservices, 1 message broker, 1 database, 100 concurrent users

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Spec-Driven Development Compliance
- [x] Specification document exists and is complete in `/specs/006-cloud-deployment/spec.md`
- [x] Plan document will be created based on spec requirements
- [ ] Tasks will be generated from plan before implementation begins

### Phase V - Part C Specific Requirements
- [x] All Kubernetes resources will be defined in Helm charts (FR-002)
- [x] Dapr sidecars will be enabled on all backend services (FR-014)
- [x] Secrets will be externalized to Kubernetes Secrets (FR-018)
- [x] Infrastructure will be cloud-agnostic (FR-044, FR-045, FR-046)
- [x] Kafka will be deployed with production-grade configuration (FR-010)
- [x] Deployment will be fully automated via Helm commands (FR-039)
- [x] Environment separation will be supported via Helm values files (FR-021)
- [x] Resource requests and limits will be defined for all pods (FR-026)

### Technology Stack Verification (Application Layer - Already Implemented)
- [x] Frontend uses Next.js 16+ with App Router (Phase II)
- [x] Backend uses FastAPI framework (Phase II)
- [x] SQLModel ORM used for database operations (Phase II)
- [x] Neon Serverless PostgreSQL is the database (Phase II)
- [x] Better Auth used for JWT-based authentication (Phase II)
- [x] REST API design followed (Phase II)

### Security Requirements Check
- [x] Secrets stored in Kubernetes Secrets, not in code (FR-018, FR-020)
- [x] JWT secret shared via environment variables (FR-019)
- [x] No hardcoded secrets in source code (FR-020)
- [x] Backend services restricted to internal access only (FR-023)
- [x] Frontend exposed via Ingress/LoadBalancer for public access (FR-022)

### Architecture Requirements
- [x] Services deployed independently (FR-003)
- [x] Dapr enabled on all backend services (FR-014)
- [x] Event-driven architecture preserved from Phase V - Part B
- [x] Existing application code remains unchanged (deployment focus only)

## Project Structure

### Documentation (this feature)

```text
specs/006-cloud-deployment/
├── plan.md              # This file (deployment strategy)
├── spec.md              # Feature specification (WHAT to deploy)
├── research.md          # Phase 0: Cloud deployment research
├── deployment-guide.md  # Phase 1: Step-by-step deployment runbook
├── helm-values-schema.md # Phase 1: Helm values documentation
└── tasks.md             # Phase 2: Deployment task breakdown (/sp.tasks)
```

### Helm Charts Structure (repository root)

```text
helm/
├── todo-app/                    # Umbrella chart for entire application
│   ├── Chart.yaml              # Chart metadata and dependencies
│   ├── values.yaml             # Default values (Minikube)
│   ├── values-dev.yaml         # Development environment overrides
│   ├── values-staging.yaml     # Staging environment overrides
│   ├── values-prod.yaml        # Production environment overrides
│   ├── templates/
│   │   ├── namespace.yaml      # Namespace definition
│   │   ├── secrets.yaml        # Secret templates (values from external source)
│   │   └── configmap.yaml      # Shared configuration
│   └── charts/                 # Subcharts (dependencies)
│       ├── frontend/           # Frontend service chart
│       ├── backend/            # Backend service chart
│       ├── recurring-task-service/  # Recurring task service chart
│       ├── notification-service/    # Notification service chart
│       ├── kafka/              # Kafka chart
│       └── dapr-components/    # Dapr component configurations
│
├── frontend/                    # Frontend Helm chart
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
│       ├── deployment.yaml     # Frontend deployment
│       ├── service.yaml        # Frontend service (LoadBalancer/Ingress)
│       ├── ingress.yaml        # Ingress rules for public access
│       └── hpa.yaml            # Horizontal Pod Autoscaler (optional)
│
├── backend/                     # Backend Helm chart
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
│       ├── deployment.yaml     # Backend deployment with Dapr annotations
│       ├── service.yaml        # Backend service (ClusterIP)
│       └── configmap.yaml      # Backend-specific config
│
├── recurring-task-service/      # Recurring Task Service Helm chart
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
│       ├── deployment.yaml     # Deployment with Dapr annotations
│       └── service.yaml        # Service (ClusterIP)
│
├── notification-service/        # Notification Service Helm chart
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
│       ├── deployment.yaml     # Deployment with Dapr annotations
│       └── service.yaml        # Service (ClusterIP)
│
├── kafka/                       # Kafka Helm chart
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
│       ├── zookeeper-statefulset.yaml
│       ├── zookeeper-service.yaml
│       ├── kafka-statefulset.yaml
│       ├── kafka-service.yaml
│       └── pvc.yaml            # PersistentVolumeClaims
│
└── dapr-components/             # Dapr Components Helm chart
    ├── Chart.yaml
    ├── values.yaml
    └── templates/
        ├── pubsub-kafka.yaml   # Dapr Pub/Sub component (CRD)
        └── statestore.yaml     # Dapr State Store component (optional)
```

### Deployment Scripts

```text
scripts/
├── deploy-to-cloud.sh          # Main deployment orchestration script
├── install-dapr.sh             # Dapr installation script
├── create-secrets.sh           # Secret creation helper
├── validate-deployment.sh      # Post-deployment validation
└── rollback.sh                 # Rollback helper script
```

**Structure Decision**: This is a deployment-focused phase, so the structure centers on Helm charts rather than application code. We'll create an umbrella chart (`todo-app`) that orchestrates all subcharts, allowing independent deployment of each service while maintaining a single entry point for full-stack deployment. Each service gets its own Helm chart for maximum flexibility and reusability.

## Complexity Tracking

> **No violations detected** - All deployment work aligns with Phase V - Part C constitution principles.

---

## Phase 0: Research & Decision Making

### Research Areas

1. **Cloud Kubernetes Cluster Setup**
   - Oracle Cloud Kubernetes Engine (OKE) setup and configuration
   - Azure Kubernetes Service (AKS) setup and configuration
   - Google Kubernetes Engine (GKE) setup and configuration
   - Common cluster requirements (node pools, networking, storage classes)
   - kubectl context configuration for multiple clusters

2. **Helm Chart Best Practices**
   - Helm 3.x chart structure and conventions
   - Umbrella charts vs independent charts
   - Values file organization (default, dev, staging, prod)
   - Chart dependencies and version management
   - Helm hooks for pre/post-deployment tasks
   - Chart testing and validation strategies

3. **Dapr Installation on Kubernetes**
   - Dapr CLI installation methods (`dapr init -k`)
   - Dapr control plane components (operator, sidecar-injector, sentry, placement)
   - Dapr component CRD configuration
   - Dapr sidecar injection via annotations
   - Dapr telemetry and observability configuration

4. **Kafka Deployment Strategies**
   - Kafka StatefulSet configuration for Kubernetes
   - Zookeeper vs KRaft mode for Kafka coordination
   - PersistentVolume configuration for Kafka data
   - Kafka resource requirements (CPU, memory, storage)
   - Kafka topic creation and management
   - Kafka monitoring and health checks

5. **Secrets Management**
   - Kubernetes Secrets creation and management
   - External secrets management (Sealed Secrets, External Secrets Operator)
   - Secret rotation strategies
   - Environment variable injection from Secrets
   - Secret encryption at rest

6. **Ingress and Load Balancing**
   - Ingress controller options (Nginx, Traefik, cloud-native)
   - LoadBalancer service type for cloud providers
   - DNS configuration and domain mapping
   - TLS/SSL certificate management (optional for Phase V - Part C)

7. **Resource Management**
   - Resource requests and limits best practices
   - Horizontal Pod Autoscaler (HPA) configuration
   - Vertical Pod Autoscaler (VPA) considerations
   - Resource quotas and limit ranges
   - Node affinity and pod anti-affinity

8. **Deployment Validation**
   - Health check endpoint design
   - Liveness and readiness probe configuration
   - Deployment rollout strategies (RollingUpdate, Recreate)
   - Rollback procedures and Helm history
   - Smoke testing and integration testing post-deployment

### Key Decisions

**Decision 1: Helm Chart Organization**
- **Chosen**: Umbrella chart with subcharts for each service
- **Rationale**: Allows both full-stack deployment (`helm install todo-app`) and independent service deployment (`helm install backend`). Maximizes flexibility while maintaining simplicity.
- **Alternatives Considered**:
  - Single monolithic chart: Rejected due to lack of independent deployment capability
  - Completely independent charts: Rejected due to complexity in managing shared configuration

**Decision 2: Dapr Installation Approach**
- **Chosen**: Dapr CLI (`dapr init -k`) for initial installation, Helm for upgrades
- **Rationale**: Dapr CLI is the official recommended method and handles all control plane components automatically. Helm can be used for version upgrades.
- **Alternatives Considered**:
  - Dapr Helm chart directly: Rejected due to additional complexity and non-standard approach
  - Operator-based installation: Rejected as overkill for current scope

**Decision 3: Kafka Deployment Strategy**
- **Chosen**: Custom Kafka StatefulSet with Zookeeper (reuse Phase V - Part B manifests, wrap in Helm)
- **Rationale**: We already have working Kafka manifests from Part B. Wrapping them in Helm provides templating and values management without reinventing the wheel.
- **Alternatives Considered**:
  - Bitnami Kafka Helm chart: Rejected due to complexity and learning curve
  - Strimzi Kafka Operator: Rejected as overkill for current scope
  - Cloud-managed Kafka: Rejected to maintain cloud-agnostic approach

**Decision 4: Secrets Management Approach**
- **Chosen**: Kubernetes Secrets with manual creation via script, values referenced in Helm
- **Rationale**: Simple, cloud-agnostic, and sufficient for Phase V - Part C scope. Secrets created once per environment, referenced in Helm values.
- **Alternatives Considered**:
  - Sealed Secrets: Rejected as additional complexity for current scope
  - External Secrets Operator: Rejected as requires external secret store setup
  - Helm secrets plugin: Rejected due to additional tooling dependency

**Decision 5: Frontend Access Strategy**
- **Chosen**: Kubernetes LoadBalancer service type for cloud, Ingress for advanced routing (optional)
- **Rationale**: LoadBalancer is simplest for cloud providers and automatically provisions external IP. Ingress can be added later for path-based routing or TLS.
- **Alternatives Considered**:
  - NodePort: Rejected as not production-grade
  - Ingress only: Rejected as requires additional Ingress controller setup

**Decision 6: Environment Configuration Strategy**
- **Chosen**: Separate Helm values files per environment (values-dev.yaml, values-staging.yaml, values-prod.yaml)
- **Rationale**: Clear separation of environment-specific configuration, easy to version control and review changes.
- **Alternatives Considered**:
  - Single values file with conditionals: Rejected due to complexity and error-prone
  - Environment variables only: Rejected as doesn't leverage Helm's templating power

**Decision 7: Deployment Order**
- **Chosen**: Sequential deployment with validation checkpoints
  1. Namespace and Secrets
  2. Dapr control plane
  3. Kafka and Zookeeper
  4. Dapr components (Pub/Sub)
  5. Backend services (backend, recurring-task-service, notification-service)
  6. Frontend service
- **Rationale**: Dependencies must be deployed before dependents. Validation at each step prevents cascading failures.
- **Alternatives Considered**:
  - Parallel deployment: Rejected due to dependency conflicts
  - Single Helm install: Rejected as doesn't allow validation checkpoints

**Decision 8: Rollback Strategy**
- **Chosen**: Helm rollback command with history tracking
- **Rationale**: Helm maintains release history automatically, rollback is single command. Simple and reliable.
- **Alternatives Considered**:
  - Manual kubectl apply of previous manifests: Rejected as error-prone
  - GitOps-based rollback: Rejected as requires CI/CD setup (out of scope)

---

## Phase 1: Design Artifacts

### Deployment Guide (deployment-guide.md)

**Purpose**: Step-by-step runbook for deploying the Todo application to a cloud Kubernetes cluster.

**Contents**:
1. Prerequisites checklist (kubectl, Helm, Dapr CLI, cluster access)
2. Cluster preparation steps (namespace creation, RBAC setup)
3. Secrets creation procedure (database credentials, JWT secret)
4. Dapr installation steps
5. Helm chart deployment sequence
6. Validation procedures for each component
7. Troubleshooting common issues
8. Rollback procedures

### Helm Values Schema (helm-values-schema.md)

**Purpose**: Document all configurable values in Helm charts with types, defaults, and descriptions.

**Contents**:
1. Global values (namespace, image registry, image pull policy)
2. Frontend values (replicas, resources, ingress configuration)
3. Backend values (replicas, resources, database connection, JWT secret)
4. Recurring Task Service values (replicas, resources, database connection)
5. Notification Service values (replicas, resources)
6. Kafka values (replicas, storage size, resource limits)
7. Dapr values (log level, telemetry configuration)
8. Environment-specific overrides (dev, staging, prod)

### Deployment Contracts

**No API contracts for this phase** - This is infrastructure deployment, not feature development. The "contracts" are:
- Helm values schema (documented in helm-values-schema.md)
- Kubernetes resource specifications (defined in Helm templates)
- Deployment order and dependencies (documented in deployment-guide.md)

---

## Phase 2: Task Generation

Tasks will be generated via `/sp.tasks` command after this plan is complete. Expected task categories:

1. **Setup Tasks**: Helm chart structure creation, script setup
2. **Helm Chart Tasks**: Create charts for each service (frontend, backend, recurring-task-service, notification-service, Kafka, Dapr components)
3. **Values Configuration Tasks**: Create environment-specific values files
4. **Deployment Script Tasks**: Create deployment orchestration scripts
5. **Validation Tasks**: Create validation and testing procedures
6. **Documentation Tasks**: Create deployment guide and runbook

---

## Deployment Architecture

### Namespace Organization

```
todo-app (namespace)
├── frontend (deployment)
├── backend (deployment + dapr sidecar)
├── recurring-task-service (deployment + dapr sidecar)
├── notification-service (deployment + dapr sidecar)
├── kafka (statefulset)
├── zookeeper (statefulset)
└── secrets (kubernetes secrets)
```

### Service Communication

```
User → LoadBalancer → Frontend (Next.js)
                         ↓
Frontend → ClusterIP → Backend (FastAPI + Dapr)
                         ↓
Backend → Dapr Pub/Sub → Kafka
                         ↓
Kafka → Dapr Pub/Sub → Recurring Task Service (Dapr)
Kafka → Dapr Pub/Sub → Notification Service (Dapr)
                         ↓
All Services → ClusterIP → Neon PostgreSQL (external)
```

### Resource Allocation (Initial Estimates)

| Service | Replicas | CPU Request | CPU Limit | Memory Request | Memory Limit |
|---------|----------|-------------|-----------|----------------|--------------|
| Frontend | 2 | 100m | 500m | 128Mi | 512Mi |
| Backend | 2 | 200m | 1000m | 256Mi | 1Gi |
| Recurring Task Service | 1 | 100m | 500m | 128Mi | 512Mi |
| Notification Service | 1 | 50m | 200m | 64Mi | 256Mi |
| Kafka | 1 | 500m | 2000m | 1Gi | 4Gi |
| Zookeeper | 1 | 250m | 1000m | 512Mi | 2Gi |

**Total Cluster Requirements**: ~1.2 CPU cores, ~2.1 GB memory (minimum)

---

## Validation Criteria

### Deployment Success Criteria

1. **All pods running**: `kubectl get pods -n todo-app` shows all pods in Running state
2. **Dapr sidecars injected**: Backend services have 2 containers (app + daprd)
3. **Frontend accessible**: Public URL returns 200 OK response
4. **Backend health check**: `curl http://backend:8000/health` returns healthy status
5. **Kafka topics created**: `task-events` and `reminders` topics exist
6. **Event flow working**: Create task → event published → recurring task created
7. **Secrets loaded**: Pods can access database and JWT secret from environment variables
8. **Resource limits enforced**: Pods do not exceed defined CPU/memory limits

### Rollback Success Criteria

1. **Helm rollback completes**: `helm rollback todo-app` succeeds without errors
2. **Previous version restored**: Pods running previous image versions
3. **Services remain available**: No downtime during rollback
4. **Data integrity maintained**: No data loss during rollback

---

## Risk Analysis

### Risk 1: Cloud Provider Differences
**Impact**: High - Deployment may fail on specific cloud provider
**Mitigation**: Test on Minikube first, use cloud-agnostic Kubernetes features only, document provider-specific quirks

### Risk 2: Secrets Management Complexity
**Impact**: Medium - Incorrect secret configuration blocks deployment
**Mitigation**: Create secret creation script with validation, document secret format clearly, test secret injection

### Risk 3: Dapr Installation Failures
**Impact**: High - Without Dapr, event-driven services cannot function
**Mitigation**: Validate Dapr installation before deploying services, provide troubleshooting guide, test Dapr components independently

### Risk 4: Kafka Resource Exhaustion
**Impact**: Medium - Kafka pod crashes due to insufficient resources
**Mitigation**: Set appropriate resource limits, monitor Kafka metrics, document scaling procedures

### Risk 5: Helm Chart Errors
**Impact**: High - Syntax errors in Helm templates block deployment
**Mitigation**: Use `helm lint` and `helm template` for validation, test charts on Minikube before cloud deployment

---

## Success Metrics

- **Deployment Time**: <15 minutes from `helm install` to all services ready
- **Rollback Time**: <5 minutes from `helm rollback` to previous version restored
- **Frontend Load Time**: <3 seconds for initial page load
- **API Response Time**: <2 seconds for task CRUD operations
- **Event Processing Latency**: <5 seconds from task completion to next recurring task created
- **System Uptime**: 99.9% availability (excluding planned maintenance)
- **Resource Efficiency**: <80% CPU and memory utilization under normal load

---

## Next Steps

1. **Generate research.md**: Document detailed findings for each research area
2. **Generate deployment-guide.md**: Create step-by-step deployment runbook
3. **Generate helm-values-schema.md**: Document all Helm values with types and descriptions
4. **Run `/sp.tasks`**: Generate detailed task breakdown for implementation
5. **Run `/sp.implement`**: Execute deployment tasks and validate each step

# Implementation Plan: Local Kubernetes Deployment

**Branch**: `003-minikube-deployment` | **Date**: 2026-02-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-minikube-deployment/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Deploy the Phase III Todo Chatbot application (frontend and backend) to a local Minikube Kubernetes cluster using Helm charts for resource management. The deployment will containerize both services using Docker, expose them via Kubernetes Services, and manage all configuration through Helm. AI DevOps tools (Gordon, kubectl-ai, kagent) will be leveraged where available to automate Docker image creation and Helm chart generation. The deployment must maintain Phase III functionality without code modifications and support clean installation/uninstallation workflows.

## Technical Context

**Language/Version**: Docker 24+, Kubernetes 1.28+ (Minikube), Helm 3.12+
**Primary Dependencies**: Minikube, Docker, Helm, kubectl, kubectl-ai (optional), kagent (optional), Gordon (optional)
**Storage**: Kubernetes Secrets for sensitive data, ConfigMaps for configuration, Neon PostgreSQL (external, existing)
**Testing**: Manual deployment validation, kubectl commands, Helm test hooks
**Target Platform**: Local Minikube cluster on developer workstation
**Project Type**: Infrastructure/Deployment (containerization of existing web application)
**Performance Goals**: Pods reach Running state within 5 minutes, frontend accessible within 1 minute of pod startup
**Constraints**: No code modifications to Phase III application, deployment must work on clean Minikube cluster, Helm install/uninstall must be clean
**Scale/Scope**: 2 services (frontend, backend), 1 Helm chart, local development environment only

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Spec-Driven Development Compliance
- [x] Specification document exists and is complete in `/specs/003-minikube-deployment/spec.md`
- [x] Plan document will be created based on spec requirements
- [x] Tasks will be generated from plan before implementation begins

### Phase IV Specific Requirements
- [x] Strict spec-driven deployment workflow will be followed
- [x] No manual trial-and-error deployment will occur
- [x] Phase III application code will NOT be modified
- [x] AI DevOps tools will be used where available with documented fallbacks
- [x] Kubernetes is the single runtime target (Minikube for local)
- [x] Docker images will be immutable once built
- [x] Configuration will be externalized (ConfigMaps, Secrets)
- [x] Services will be deployable independently
- [x] Helm charts will define the deployment contract

### Technology Stack Verification (Phase III Preservation)
- [x] Frontend uses Next.js 16+ with App Router (no changes)
- [x] Backend uses FastAPI framework (no changes)
- [x] SQLModel ORM for database operations (no changes)
- [x] Neon Serverless PostgreSQL database (external, no changes)
- [x] Better Auth for JWT-based authentication (no changes)
- [x] REST API design (no changes)

### Security Requirements Check
- [x] JWT secrets will be stored in Kubernetes Secrets
- [x] Database credentials will be stored in Kubernetes Secrets
- [x] Environment variables will be injected via Kubernetes configuration
- [x] No hardcoded secrets in Docker images or Helm charts
- [x] Phase III security model remains unchanged

### Architecture Requirements
- [x] Backend and frontend will remain separate deployable services
- [x] Each service will have its own Docker image
- [x] Each service will have its own Kubernetes Deployment
- [x] Services will communicate via Kubernetes service discovery
- [x] Phase III functionality will be preserved without degradation

## Project Structure

### Documentation (this feature)

```text
specs/003-minikube-deployment/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output - Docker/Helm/K8s best practices
├── data-model.md        # Phase 1 output - Kubernetes resource relationships
├── quickstart.md        # Phase 1 output - Deployment quickstart guide
├── contracts/           # Phase 1 output - Helm values schema, resource templates
│   ├── helm-values-schema.md
│   └── kubernetes-resources.md
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Deployment artifacts (new for Phase IV)
helm/
└── todo-chatbot/
    ├── Chart.yaml           # Helm chart metadata
    ├── values.yaml          # Default configuration values
    ├── templates/
    │   ├── frontend-deployment.yaml
    │   ├── frontend-service.yaml
    │   ├── backend-deployment.yaml
    │   ├── backend-service.yaml
    │   ├── configmap.yaml
    │   └── secrets.yaml
    └── README.md

# Docker build contexts (new for Phase IV)
docker/
├── frontend/
│   ├── Dockerfile
│   └── .dockerignore
└── backend/
    ├── Dockerfile
    └── .dockerignore

# Existing application code (Phase III - NO CHANGES)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/
```

**Structure Decision**: Phase IV adds deployment infrastructure (Docker, Helm) without modifying existing Phase III application code. Docker build contexts reference existing backend/ and frontend/ directories. Helm charts manage Kubernetes resources for both services.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations. All constitution requirements are met.

## Phase 0: Research & Decisions

### Docker Containerization Strategy

**Decision**: Multi-stage Docker builds for both frontend and backend to minimize image size and separate build dependencies from runtime dependencies.

**Frontend Containerization**:
- Base image: Node.js 18 Alpine for minimal size
- Build stage: Install dependencies, build Next.js production bundle
- Runtime stage: Copy built artifacts, expose port 3000
- Environment variables: Injected at runtime via Kubernetes
- Image naming: `todo-frontend:v1.0.0`

**Backend Containerization**:
- Base image: Python 3.11 slim for minimal size
- Build stage: Install dependencies from requirements.txt
- Runtime stage: Copy application code and dependencies
- Expose port 8000 for FastAPI
- Environment variables: Injected at runtime via Kubernetes
- Image naming: `todo-backend:v1.0.0`

**Image Tagging Strategy**:
- Semantic versioning: `v<major>.<minor>.<patch>`
- Git commit SHA as additional tag for traceability
- `latest` tag for development convenience
- Immutable tags for production deployments

**Image Registry**:
- Local Minikube registry for development
- Images built and loaded directly into Minikube
- No external registry required for Phase IV

### Helm Chart Architecture

**Decision**: Single Helm chart managing both frontend and backend services with shared configuration and independent scaling capabilities.

**Chart Structure**:
- Chart name: `todo-chatbot`
- Chart version: `1.0.0`
- App version: `1.0.0` (matches Phase III)
- Dependencies: None (self-contained)

**Values Organization**:
- Global values: Shared configuration (namespace, labels)
- Frontend values: Replica count, image, resources, service config
- Backend values: Replica count, image, resources, service config
- Database values: Connection string, credentials (from Secrets)
- Auth values: JWT secret (from Secrets)

**Template Structure**:
- Separate templates for each resource type
- Consistent labeling and annotations
- ConfigMap for non-sensitive configuration
- Secrets for sensitive data (database, JWT)
- Service resources for internal communication
- Deployment resources for pod management

### Kubernetes Resource Layout

**Frontend Deployment**:
- Replicas: 1 (configurable via Helm values)
- Container: todo-frontend image
- Port: 3000
- Environment variables: API_BASE_URL (points to backend service)
- Resource limits: 512Mi memory, 500m CPU
- Liveness probe: HTTP GET /
- Readiness probe: HTTP GET /

**Frontend Service**:
- Type: NodePort (accessible from host via Minikube)
- Port: 3000
- Target port: 3000
- Selector: app=todo-frontend

**Backend Deployment**:
- Replicas: 1 (configurable via Helm values)
- Container: todo-backend image
- Port: 8000
- Environment variables: DATABASE_URL, JWT_SECRET (from Secrets)
- Resource limits: 1Gi memory, 1000m CPU
- Liveness probe: HTTP GET /health
- Readiness probe: HTTP GET /health

**Backend Service**:
- Type: ClusterIP (internal only)
- Port: 8000
- Target port: 8000
- Selector: app=todo-backend

**ConfigMap**:
- Application configuration (non-sensitive)
- Feature flags
- API endpoints

**Secrets**:
- Database connection string (DATABASE_URL)
- JWT secret (JWT_SECRET)
- Base64 encoded values

### Deployment Flow

**Prerequisites**:
1. Minikube installed and running
2. kubectl configured for Minikube context
3. Helm 3 installed
4. Docker images built and loaded into Minikube

**Deployment Steps**:
1. Start Minikube cluster: `minikube start`
2. Build Docker images for frontend and backend
3. Load images into Minikube: `minikube image load`
4. Create Kubernetes namespace (optional)
5. Install Helm chart: `helm install todo-chatbot ./helm/todo-chatbot`
6. Wait for pods to reach Running state
7. Verify deployment: `kubectl get pods,services`
8. Access frontend: `minikube service todo-frontend`

**Validation Steps**:
1. Check pod status: All pods Running
2. Check service endpoints: Services have endpoints
3. Test frontend accessibility: Browser loads UI
4. Test backend health: Health endpoint responds
5. Test end-to-end: Login, create task, verify functionality

**Rollback Strategy**:
1. Helm rollback: `helm rollback todo-chatbot`
2. Manual rollback: `kubectl rollout undo deployment/<name>`
3. Complete uninstall: `helm uninstall todo-chatbot`
4. Verify cleanup: No residual resources remain

### AI DevOps Tools Integration

**Gordon (Docker AI)**:
- Usage: Generate Dockerfiles for frontend and backend
- Prompt: "Create production-ready Dockerfile for Next.js 16 application"
- Prompt: "Create production-ready Dockerfile for FastAPI application"
- Fallback: Manual Dockerfile creation using best practices
- Validation: Build images and test locally before Minikube deployment

**kubectl-ai**:
- Usage: Generate Kubernetes resource manifests
- Prompt: "Create Deployment for Next.js frontend with health checks"
- Prompt: "Create Service to expose FastAPI backend internally"
- Usage: Debug deployment issues
- Prompt: "Why is my pod in CrashLoopBackOff state?"
- Fallback: Manual kubectl commands and manifest creation

**kagent**:
- Usage: Analyze cluster state and resource utilization
- Prompt: "Analyze resource usage for todo-chatbot deployment"
- Prompt: "Identify bottlenecks in service communication"
- Fallback: Manual kubectl commands (get, describe, logs)

**AI Tool Workflow**:
1. Use AI tools for initial generation
2. Review and validate generated artifacts
3. Test in local environment
4. Document any manual modifications required
5. Maintain fallback documentation for manual processes

### Configuration Management

**Externalization Strategy**:
- All environment-specific values in Helm values.yaml
- Sensitive data in Kubernetes Secrets
- Non-sensitive config in ConfigMaps
- No hardcoded values in Docker images or manifests

**Environment Variables**:
- Frontend: `NEXT_PUBLIC_API_BASE_URL` (backend service URL)
- Backend: `DATABASE_URL` (from Secret), `JWT_SECRET` (from Secret)
- Both: `ENVIRONMENT` (development/production)

**Secret Management**:
- Secrets created via Helm templates
- Values provided via values.yaml (base64 encoded)
- Mounted as environment variables in pods
- Never committed to version control in plain text

## Phase 1: Design & Contracts

### Kubernetes Resource Model (data-model.md)

**Entities**: Kubernetes resources and their relationships

**Frontend Deployment**:
- Manages: Frontend pods (replicas)
- References: Frontend Docker image
- Exposes: Port 3000
- Depends on: Backend Service (for API calls)

**Backend Deployment**:
- Manages: Backend pods (replicas)
- References: Backend Docker image
- Exposes: Port 8000
- Depends on: Database (external), Secrets (JWT, DB credentials)

**Frontend Service**:
- Selects: Frontend pods
- Exposes: NodePort for external access
- Routes: Traffic to frontend pods on port 3000

**Backend Service**:
- Selects: Backend pods
- Exposes: ClusterIP for internal access
- Routes: Traffic to backend pods on port 8000
- Discovered by: Frontend pods via DNS

**ConfigMap**:
- Stores: Non-sensitive configuration
- Consumed by: Frontend and Backend Deployments
- Mounted as: Environment variables or volume

**Secrets**:
- Stores: DATABASE_URL, JWT_SECRET
- Consumed by: Backend Deployment
- Mounted as: Environment variables
- Encoded: Base64

**Helm Chart**:
- Manages: All above resources
- Templated: Values injected from values.yaml
- Versioned: Chart version tracks deployment version

### Deployment Contracts (contracts/)

**Helm Values Schema**:
- Global settings (namespace, labels)
- Frontend configuration (image, replicas, resources, service)
- Backend configuration (image, replicas, resources, service)
- Database configuration (connection string)
- Authentication configuration (JWT secret)

**Kubernetes Resource Templates**:
- Deployment manifests (frontend, backend)
- Service manifests (frontend NodePort, backend ClusterIP)
- ConfigMap manifest (application config)
- Secret manifest (sensitive data)

**API Contracts** (Phase III - unchanged):
- Frontend-to-Backend: REST API over HTTP
- Backend-to-Database: PostgreSQL protocol
- Service Discovery: Kubernetes DNS (backend-service.default.svc.cluster.local)

### Quickstart Guide (quickstart.md)

**Prerequisites**:
- Minikube installed
- kubectl installed
- Helm 3 installed
- Docker installed

**Quick Deployment**:
1. Clone repository
2. Build Docker images
3. Load images into Minikube
4. Install Helm chart
5. Access application

**Verification**:
- Check pod status
- Access frontend URL
- Test application functionality

**Cleanup**:
- Uninstall Helm chart
- Stop Minikube cluster

## Phase 2: Task Breakdown

*This section will be completed by the `/sp.tasks` command.*

Tasks will be generated based on this plan and will include:
- Docker image creation for frontend and backend
- Helm chart development with all resource templates
- Minikube cluster setup and configuration
- Deployment validation and testing
- Documentation and runbook creation

## Risks & Mitigations

**Risk**: Docker images too large, slow to build/deploy
**Mitigation**: Use multi-stage builds, Alpine base images, .dockerignore files

**Risk**: Pods fail to start due to missing environment variables
**Mitigation**: Validate Secrets and ConfigMaps before deployment, use init containers if needed

**Risk**: Frontend cannot reach backend service
**Mitigation**: Use Kubernetes service discovery, verify DNS resolution, check network policies

**Risk**: AI DevOps tools unavailable or generate incorrect artifacts
**Mitigation**: Document manual fallback processes, validate all generated artifacts before use

**Risk**: Helm chart installation fails mid-deployment
**Mitigation**: Use Helm hooks for ordered deployment, implement rollback strategy

**Risk**: Phase III functionality breaks in containerized environment
**Mitigation**: Thorough testing in Minikube before considering deployment complete, no code modifications

## Success Criteria Mapping

- **SC-001**: Helm installation < 5 minutes → Optimized Docker images, efficient Helm templates
- **SC-002**: Pods Running < 5 minutes → Fast image pulls, proper resource limits, health checks
- **SC-003**: Frontend accessible < 1 minute → NodePort service, readiness probes
- **SC-004**: Backend health check < 30 seconds → Liveness/readiness probes configured
- **SC-005**: 100% API success rate → Proper service discovery, network configuration
- **SC-006**: 0 pod restarts in 30 minutes → Stable images, correct resource limits, proper configuration
- **SC-007**: Helm uninstall < 2 minutes → Clean resource definitions, no orphaned resources
- **SC-008**: Reinstall identical to initial → Idempotent Helm charts, no state dependencies
- **SC-009**: Phase III features work → No code modifications, proper environment configuration
- **SC-010**: Repeatable deployment → Documented process, version-controlled artifacts

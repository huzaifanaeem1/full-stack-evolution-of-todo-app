<!-- SYNC IMPACT REPORT:
Version change: 1.3.0 -> 1.4.0
Modified principles: None
Added sections:
- Phase V - Part C: Production Cloud Deployment Principles (new section)
- Phase V - Part C: Architecture Principles (new section)
- Phase V - Part C: Scope Boundaries (new section)
- Strict Helm-Based Deployment (NON-NEGOTIABLE) (new principle)
- Dapr-Enabled Services Mandate (new principle)
- Secrets Externalization Requirement (new principle)
- Cloud-Agnostic Infrastructure (new principle)
- Production-Grade Kafka Configuration (new principle)
- Reproducible Deployment Process (new principle)
- Environment Separation (new principle)
- Resource Management and Limits (new principle)
- Helm Chart Structure and Organization (new principle)
- Dapr Component Configuration (new principle)
- Service Discovery and Networking (new principle)
- Observability and Monitoring (new principle)
- Database and State Management (new principle)
Removed sections: None
Templates requiring updates:
- .specify/templates/plan-template.md: ⚠ pending (may need Phase V - Part C constitution checks for Helm and cloud deployment)
- .specify/templates/spec-template.md: ✅ reviewed (no changes needed)
- .specify/templates/tasks-template.md: ⚠ pending (may need Phase V - Part C deployment task patterns)
- .specify/templates/commands/*.md: ✅ reviewed (no changes needed)
Follow-up TODOs:
- Consider adding Phase V - Part C specific constitution checks to plan-template.md for Helm chart validation
- Verify Helm chart structure aligns with Kubernetes principles from Phase IV
- Ensure Dapr component configuration patterns are documented in task templates
- Validate secrets management approach across all deployment templates
-->

# Todo Full-Stack Web Application Constitution

## Core Principles

### Strict Spec-Driven Development (NON-NEGOTIABLE)
Every feature follows the Specify → Plan → Tasks → Implement sequence; Specifications must be complete before planning begins; Plans must be approved before implementation starts; No implementation without corresponding tasks.

### No Manual Coding by User (NON-NEGOTIABLE)
All code must be generated through automated processes; Users interact only through specifications, plans, and task definitions; Manual code changes are prohibited unless through automated generation tools.

### Phase Separation: CLI vs Web Application
Phase I (CLI) and Phase II (Full-Stack Web App) are completely separate implementations; Codebases, repositories, and architectures must remain independent; No code sharing between phases unless through well-defined libraries.

### Separate Backend and Frontend Services
Backend and frontend must be developed as separate deployable services; Clear API contracts define communication between services; Each service has independent scaling and deployment capabilities.

### Mandatory Authentication
Every endpoint and feature must require user authentication; No anonymous access allowed except health/status endpoints; Authentication must be implemented using Better Auth (JWT-based).

### User-Isolated Data Access
Users can only access their own data; No cross-user data visibility or manipulation allowed; All database queries must include user-id filters for security.

## Technology Stack Requirements

### Frontend: Next.js 16+ (App Router)
Frontend must use Next.js version 16 or higher with App Router architecture; Strict adherence to App Router patterns and conventions; Client-side and server-side rendering capabilities leveraged appropriately.

### Backend: FastAPI (Python)
Backend services must be built using FastAPI framework; Python type hints utilized for automatic API documentation; Pydantic models for request/response validation.

### ORM: SQLModel
Database operations must use SQLModel ORM; Models must inherit from SQLModel's base classes; Proper relationship definitions and foreign key constraints enforced.

### Database: Neon Serverless PostgreSQL
Database layer must use Neon Serverless PostgreSQL; Connection pooling and optimization for serverless environments; Proper schema migrations and versioning.

### Authentication: Better Auth (JWT-based)
Authentication system must use Better Auth library; JWT tokens for session management; Consistent JWT secret shared between frontend and backend via environment variables.

### API: REST Only
API endpoints must follow RESTful conventions; No GraphQL, gRPC, or other protocols allowed; Standard HTTP methods and status codes.

## Security Requirements

### JWT Token Verification
All API endpoints must verify JWT tokens before processing requests; Token verification must include signature validation and expiration checks; Proper error handling for invalid/expired tokens.

### User ID Extraction from Token
User ID must be consistently extracted from JWT payload; All user-specific operations must use the extracted user ID; No alternative user identification mechanisms.

### Task Isolation by User
Users can only access, modify, or delete their own tasks; Database queries must include user_id filters; API endpoints must validate user ownership before operations.

### Environment Variable Security
JWT secret must be shared via environment variables only; No hardcoded secrets in source code; Proper environment variable validation and error handling.

## Non-Negotiable Constraints

### No AI Features in Phase II
No artificial intelligence capabilities in Phase II implementation; AI features reserved for future phases only; Current scope limited to core todo functionality.

### No UI Overengineering
Simple, functional UI design prioritized over complex interfaces; Minimal styling and components; Focus on core functionality over visual enhancements.

### Scope Limitation
Implementation restricted to requirements specified in the constitution; No additional features beyond specified requirements; Feature creep strictly prohibited.

### Consistent JWT Secret Sharing
Same JWT secret must be used across frontend and backend; Secure transmission and storage of the secret; Proper environment configuration for both services.

## Phase IV: Local Kubernetes Deployment Principles

### Strict Spec-Driven Deployment (NON-NEGOTIABLE)
All deployment work must follow Specify → Plan → Tasks → Implement sequence; No deployment action may occur without an approved task; No Kubernetes or Docker configuration may be written without specification; Skipping any step is strictly forbidden.

### No Manual Trial-and-Error Deployment
Manual trial-and-error deployment is strictly prohibited; All deployment steps must be planned and documented; Configuration changes must be version-controlled and reviewed; Improvisation without documentation is forbidden.

### Existing Application Code Immutability
Phase III application code must not be modified during Phase IV; Deployment focuses on infrastructure automation only; No feature changes or code refactoring allowed; Phase III functionality must remain unchanged.

### AI DevOps Tools Integration
Docker images must be generated via AI agents where possible; Helm charts must be generated via kubectl-ai or kagent where possible; AI DevOps tools assist but do not replace validation; If Gordon or other AI tools are unavailable, fallback must be documented, not improvised.

### Kubernetes as Single Runtime Target
Kubernetes is the single runtime target for deployment; All services must be deployable on Kubernetes clusters; Minikube used for local development and testing; No alternative container orchestration platforms.

### Docker Image Immutability
Docker images must be immutable once built; No runtime modifications to container images; Version tags must be explicit and meaningful; Image rebuilds required for any changes.

### Configuration Externalization
All configuration must be externalized from application code; Environment variables, ConfigMaps, and Secrets used for configuration; No hardcoded configuration in Docker images; Configuration changes must not require image rebuilds.

### Independent Service Deployment
Services must be deployable independently; Frontend, backend, and database as separate deployable units; Each service has its own Helm chart or deployment manifest; Service dependencies managed through Kubernetes service discovery.

### Helm Charts as Deployment Contract
Helm charts define the deployment contract for all services; Charts must be version-controlled and documented; Chart values must be externalized for environment-specific configuration; Helm used as the primary deployment mechanism.

## Phase IV: Scope Boundaries

### In Scope for Phase IV
Dockerizing frontend and backend applications; Creating Helm charts for all services; Deploying to local Minikube cluster; AI-assisted Docker and Kubernetes operations; Infrastructure automation and deployment discipline.

### Out of Scope for Phase IV
Feature changes or enhancements; Kafka or Dapr integration; Cloud provider deployments (AWS, GCP, Azure); CI/CD pipeline implementation; Application code modifications.

## Phase V - Part A: Advanced and Intermediate Features Principles

### Strict Spec-Driven Development for Features (NON-NEGOTIABLE)
All Phase V - Part A work must follow the exact sequence: Specify → Plan → Tasks → Implement; No code may be written without an approved task; Every task must trace back to a specification item; No feature may be added unless explicitly specified; Skipping or combining steps is strictly forbidden.

### Application-Level Focus Only
Phase V - Part A focuses strictly on application-level behavior and intelligence; No infrastructure changes allowed (Kubernetes, Docker, Helm remain unchanged); No Kafka, Dapr, or cloud deployment logic permitted; Existing Phase I-IV functionality must not break; All enhancements are feature additions to the existing deployed system.

### Feature Traceability Mandate
Every feature implementation must trace back to specification; No feature may be added unless explicitly specified in Phase V - Part A spec; Ambiguity must result in stopping and asking clarifying questions; Manual coding is discouraged; agents must be used for implementation.

### Backward Compatibility Guarantee
All existing Phase I-IV functionality must continue to work; No breaking changes to existing APIs or data models; New features must be additive only; Existing user data and workflows must remain intact.

## Phase V - Part A: Scope Boundaries

### In Scope for Phase V - Part A
Task priorities (high, medium, low priority levels); Tags and categories for task organization; Search, filter, and sort capabilities for tasks; Due dates and deadline management; Recurring tasks (business logic only, no notification infrastructure); Advanced task organization and intelligent behavior; API enhancements for new features; AI chatbot integration for new capabilities.

### Out of Scope for Phase V - Part A
Kafka message broker integration; Dapr sidecar or service mesh; Push notifications or email notifications; Cloud deployment changes (AWS, GCP, Azure); Kubernetes configuration modifications; Docker image changes; Helm chart updates; Infrastructure or deployment changes of any kind; Breaking changes to existing Phase I-IV features.

## Phase V - Part B: Event-Driven Architecture with Kafka and Dapr Principles

### Strict Spec-Driven Event Architecture (NON-NEGOTIABLE)
All Phase V - Part B work must follow the exact sequence: Specify → Plan → Tasks → Implement; No event or service may be created without specification; No Kafka topic may exist unless specified in the specification document; Every event schema must be documented before implementation; Skipping or merging steps is strictly forbidden.

### Event-First Communication Mandate
Services must communicate via events, not direct calls; Event producers must not depend on consumers; Synchronous HTTP calls between services are prohibited where events are applicable; Dapr Pub/Sub must be used as the abstraction layer for event communication; Manual wiring of Kafka clients is discouraged when Dapr is applicable.

### Dapr as Infrastructure Abstraction
Dapr must be used as the abstraction layer wherever possible; Dapr sidecars handle infrastructure concerns (pub/sub, state, bindings); Application code must not contain Kafka-specific client logic when Dapr can abstract it; Dapr components define infrastructure bindings declaratively; Services remain portable across infrastructure changes through Dapr abstraction.

### Event Consumer Idempotency Requirement
Event consumers must be idempotent; Processing the same event multiple times must produce the same result; Event handlers must handle duplicate deliveries gracefully; State changes must be designed for at-least-once delivery semantics; No side effects that cannot be safely repeated.

### Service Statelessness and Isolation
Services must be stateless; All state must be externalized to databases or state stores; Failures must be isolated to individual services; One service failure must not cascade to others; Services scale independently based on event load.

### Event Immutability Guarantee
Events are immutable once published; No modification or deletion of published events allowed; Event versioning must be used for schema evolution; New event versions must be backward compatible or handled explicitly; Event sourcing principles apply where events represent facts.

### Existing Feature Preservation
Existing Part A features must not be modified during Part B implementation; Event-driven architecture is additive, not replacement; Synchronous REST APIs remain for client-facing operations; Internal service communication transitions to events; User-facing functionality must remain unchanged.

### No Cloud-Specific Logic
No cloud provider-specific deployment logic allowed; Infrastructure must remain cloud-agnostic through Dapr; Kafka and Dapr configurations must work on any Kubernetes cluster; No AWS, GCP, or Azure-specific services or APIs; Local development must use Minikube with same configurations.

### Ambiguity Resolution Protocol
Ambiguity must result in stopping and requesting clarification; No guessing about event schemas, topic names, or service boundaries; Agent must ask explicit questions when specifications are unclear; Manual trial-and-error is prohibited; All decisions must be documented in specifications.

## Phase V - Part B: Architecture Principles

### Event Producer Independence
Event producers must not depend on consumers; Producers publish events without knowledge of subscribers; Adding or removing consumers must not require producer changes; Loose coupling enforced through event-driven design; Services discover events through topic subscriptions, not direct references.

### Asynchronous Task Processing
Core operations publish events for asynchronous processing; Long-running tasks must be handled by specialized consumer services; Synchronous request-response limited to user-facing APIs; Background processing decoupled from user requests; Event-driven workflows enable scalability and resilience.

### Service Separation and Boundaries
Services must be separated by business capability; Each service owns its domain events and data; Clear bounded contexts define service responsibilities; No shared databases between services; Inter-service communication only through events.

### Failure Isolation and Recovery
Failures must be isolated to individual services; Dead letter queues handle failed event processing; Retry policies defined per consumer; Circuit breakers prevent cascade failures; Observability enables failure detection and diagnosis.

## Phase V - Part B: Scope Boundaries

### In Scope for Phase V - Part B
Kafka topics and event schemas; Event publishing from core services; Event consumption by specialized services; Dapr Pub/Sub component configuration; Asynchronous task processing workflows; Service separation and decoupling; Event-driven architecture patterns; Kafka and Dapr deployment on Kubernetes; Local development with Minikube and Dapr.

### Out of Scope for Phase V - Part B
Cloud provider-specific deployments (AWS, GCP, Azure); CI/CD pipeline implementation; Monitoring and observability stacks (Prometheus, Grafana); UI changes or frontend modifications; Breaking changes to existing Part A features; Real-time push notifications to clients; Email or SMS notification infrastructure; Production-grade Kafka cluster management.

## Phase V - Part C: Production Cloud Deployment Principles

### Strict Helm-Based Deployment (NON-NEGOTIABLE)
All Kubernetes resources must be defined in Helm charts; No raw kubectl apply commands for production resources; Helm charts must be version-controlled and parameterized; Values files must separate environment-specific configuration; Chart dependencies must be explicitly declared and managed.

### Dapr-Enabled Services Mandate
All microservices must have Dapr sidecars enabled; Dapr annotations must be present in all deployment manifests; Dapr components must be deployed before application services; Service-to-service communication must use Dapr APIs; No direct Kafka client usage in application code.

### Secrets Externalization Requirement
No hardcoded secrets in any configuration files; Kubernetes Secrets must be used for sensitive data; Environment variables must reference Secrets, not contain values; Database credentials, JWT secrets, API keys must be externalized; Secrets must never be committed to version control.

### Cloud-Agnostic Infrastructure
Infrastructure must work on any Kubernetes cluster (Minikube, GKE, EKS, AKS); No cloud provider-specific APIs or services in application code; Storage, networking, and compute must use Kubernetes abstractions; Helm charts must be portable across cloud providers; Local development must mirror production architecture.

### Production-Grade Kafka Configuration
Kafka must be deployed with replication and persistence; Zookeeper or KRaft mode for Kafka coordination; Proper resource limits and requests for Kafka pods; Topic configuration must support production workloads; Kafka must be accessible to all Dapr-enabled services.

### Reproducible Deployment Process
Deployment must be fully automated via Helm commands; No manual kubectl edits or patches allowed; All configuration changes must go through Helm values; Rollback must be possible via Helm history; Deployment steps must be documented and repeatable.

### Environment Separation
Development, staging, and production environments must be separate; Each environment has its own Helm values file; No shared resources between environments; Environment-specific configuration must be externalized; Promotion between environments must be controlled.

### Resource Management and Limits
All pods must have resource requests and limits defined; CPU and memory allocations must be appropriate for workload; Horizontal Pod Autoscaling (HPA) configured where applicable; Resource quotas enforced at namespace level; No unbounded resource consumption allowed.

## Phase V - Part C: Architecture Principles

### Helm Chart Structure and Organization
One Helm chart per microservice or logical component; Chart dependencies managed via Chart.yaml requirements; Shared configuration via library charts or subcharts; Values schema validation for type safety; Chart versioning follows semantic versioning.

### Dapr Component Configuration
Dapr components deployed as Kubernetes CRDs; Component configuration externalized via ConfigMaps; Pub/Sub, State Store, Bindings defined declaratively; Component scoping limits access to authorized services; Component versioning and updates managed via Helm.

### Service Discovery and Networking
Kubernetes Services for internal service discovery; Ingress controllers for external access; Network policies for service-to-service communication; DNS-based service resolution; No hardcoded IP addresses or hostnames.

### Observability and Monitoring
Structured logging to stdout/stderr for log aggregation; Health check endpoints for liveness and readiness probes; Metrics exposed for Prometheus scraping; Distributed tracing via Dapr telemetry; Centralized logging and monitoring infrastructure.

### Database and State Management
Database deployed as StatefulSet or external managed service; Persistent volumes for stateful workloads; Database migrations managed via init containers or jobs; Connection pooling and retry logic in application; Database credentials via Kubernetes Secrets.

## Phase V - Part C: Scope Boundaries

### In Scope for Phase V - Part C
Helm chart creation for all services; Dapr installation and configuration on Kubernetes; Kafka deployment with Helm; Secrets management with Kubernetes Secrets; Production-grade resource configuration; Cloud-agnostic Kubernetes deployment; Environment-specific values files; Service discovery and networking setup; Database deployment and persistence; Observability and health checks.

### Out of Scope for Phase V - Part C
Feature development or business logic changes; UI modifications or frontend enhancements; CI/CD pipeline implementation; Cloud provider-specific services (RDS, Cloud SQL, etc.); Monitoring stack deployment (Prometheus, Grafana); Certificate management and TLS configuration; Backup and disaster recovery procedures; Performance testing and load testing; Security scanning and vulnerability assessment.

## Development Workflow

### Test-First Approach
Tests must be written before implementation code; Unit, integration, and end-to-end tests required; Test coverage metrics maintained and enforced.

### Continuous Integration
Automated testing required for all code changes; Build and deployment pipelines must pass all tests; Code quality gates enforced through CI/CD.

### Code Review Standards
All changes must undergo peer review; Security and architecture compliance verified; Documentation updates included in all pull requests.

## Governance

All development must comply with this constitution; Amendments require formal approval process; Code reviews must verify constitution compliance; Deviations require explicit exception approval; Phase IV deployment must follow strict Spec-Driven Development discipline; Agent behavior must stop and ask for clarification when encountering ambiguity rather than guessing or inventing configuration.

**Version**: 1.4.0 | **Ratified**: 2026-01-09 | **Last Amended**: 2026-02-09
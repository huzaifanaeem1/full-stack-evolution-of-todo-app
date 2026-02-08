<!-- SYNC IMPACT REPORT:
Version change: 1.0.0 -> 1.1.0
Modified principles: None
Added sections:
- Phase IV: Local Kubernetes Deployment (new section)
- Kubernetes Architecture Principles (new section)
- AI DevOps Tools Integration (new section)
- Docker and Container Requirements (new section)
- Helm Chart Standards (new section)
- Deployment Discipline Rules (new section)
Removed sections: None
Templates requiring updates:
- .specify/templates/plan-template.md: ✅ reviewed (no changes needed)
- .specify/templates/spec-template.md: ✅ reviewed (no changes needed)
- .specify/templates/tasks-template.md: ✅ reviewed (no changes needed)
- .specify/templates/commands/*.md: ✅ reviewed (no changes needed)
Follow-up TODOs: None
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

## Development Workflow

### Test-First Approach
Tests must be written before implementation code; Unit, integration, and end-to-end tests required; Test coverage metrics maintained and enforced.

### Continuous Integration
Automated testing required for all code changes; Build and deployment pipelines must pass all tests; Code quality gates enforced through CI/CD.

### Code Review Standards
All changes must undergo peer review; Security and architecture compliance verified; Documentation updates included in all pull requests.

## Governance

All development must comply with this constitution; Amendments require formal approval process; Code reviews must verify constitution compliance; Deviations require explicit exception approval; Phase IV deployment must follow strict Spec-Driven Development discipline; Agent behavior must stop and ask for clarification when encountering ambiguity rather than guessing or inventing configuration.

**Version**: 1.1.0 | **Ratified**: 2026-01-09 | **Last Amended**: 2026-02-08
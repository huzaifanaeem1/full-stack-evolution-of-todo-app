# Research & Decisions: Local Kubernetes Deployment

**Feature**: 003-minikube-deployment
**Date**: 2026-02-08
**Purpose**: Document research findings and architectural decisions for Phase IV deployment

## Docker Containerization Research

### Decision: Multi-Stage Docker Builds

**Rationale**:
- Separates build dependencies from runtime dependencies
- Reduces final image size by 60-70%
- Improves security by excluding build tools from production images
- Industry standard for production containerization

**Alternatives Considered**:
- Single-stage builds: Rejected due to large image sizes and security concerns
- Distroless images: Considered but rejected for Phase IV due to debugging complexity in local development

**Best Practices Applied**:
- Use official base images (node:18-alpine, python:3.11-slim)
- Leverage Docker layer caching for faster builds
- Use .dockerignore to exclude unnecessary files
- Run containers as non-root users
- Implement health checks in Dockerfiles

### Image Tagging Strategy

**Decision**: Semantic versioning with Git SHA tags

**Rationale**:
- Semantic versioning (v1.0.0) provides clear version progression
- Git commit SHA enables traceability to source code
- Immutable tags prevent accidental overwrites
- Supports rollback to specific versions

**Implementation**:
- Primary tag: `v<major>.<minor>.<patch>` (e.g., v1.0.0)
- Secondary tag: Git commit SHA (e.g., abc123f)
- Development tag: `latest` (mutable, for convenience)

## Helm Chart Architecture Research

### Decision: Single Umbrella Chart

**Rationale**:
- Simplifies deployment (single `helm install` command)
- Manages related services as a cohesive unit
- Enables shared configuration and secrets
- Reduces operational complexity for local development

**Alternatives Considered**:
- Separate charts per service: Rejected due to increased complexity for 2-service deployment
- Helm dependencies: Rejected as overkill for tightly coupled frontend/backend

**Best Practices Applied**:
- Use Helm templates for all Kubernetes resources
- Externalize all configuration via values.yaml
- Implement proper labeling and annotations
- Use Helm hooks for ordered deployment if needed
- Version chart independently from application

### Values Organization

**Decision**: Hierarchical values structure

**Structure**:
```yaml
global:
  namespace: default
  labels: {}

frontend:
  image:
    repository: todo-frontend
    tag: v1.0.0
  replicas: 1
  resources: {}
  service:
    type: NodePort
    port: 3000

backend:
  image:
    repository: todo-backend
    tag: v1.0.0
  replicas: 1
  resources: {}
  service:
    type: ClusterIP
    port: 8000

secrets:
  databaseUrl: ""  # base64 encoded
  jwtSecret: ""    # base64 encoded
```

## Kubernetes Resource Layout Research

### Decision: Standard Deployment + Service Pattern

**Rationale**:
- Industry-standard pattern for stateless applications
- Supports horizontal scaling (though not used in Phase IV)
- Enables rolling updates and rollbacks
- Integrates with Kubernetes service discovery

**Resource Specifications**:

**Deployments**:
- Use Deployment controller (not StatefulSet - no persistent state)
- Configure resource limits to prevent resource exhaustion
- Implement liveness and readiness probes
- Use rolling update strategy (default)

**Services**:
- Frontend: NodePort for external access via Minikube
- Backend: ClusterIP for internal-only access
- Use label selectors to route traffic to pods

**ConfigMaps & Secrets**:
- ConfigMap for non-sensitive configuration
- Secrets for DATABASE_URL and JWT_SECRET
- Mount as environment variables (not volumes)

### Health Check Strategy

**Decision**: HTTP-based health checks

**Frontend**:
- Liveness probe: GET / (checks if Next.js is responding)
- Readiness probe: GET / (checks if app is ready to serve traffic)
- Initial delay: 10 seconds
- Period: 10 seconds

**Backend**:
- Liveness probe: GET /health (checks if FastAPI is alive)
- Readiness probe: GET /health (checks if app can handle requests)
- Initial delay: 15 seconds (allows DB connection setup)
- Period: 10 seconds

## Minikube Deployment Flow Research

### Decision: Image Loading via Minikube

**Rationale**:
- No external registry required for local development
- Faster than pushing/pulling from remote registry
- Simpler setup for developers
- Minikube provides built-in image loading

**Alternatives Considered**:
- Local Docker registry: Rejected as unnecessary complexity
- DockerHub: Rejected to avoid external dependencies
- Minikube registry addon: Considered but image loading is simpler

**Implementation**:
```bash
# Build images locally
docker build -t todo-frontend:v1.0.0 ./docker/frontend
docker build -t todo-backend:v1.0.0 ./docker/backend

# Load into Minikube
minikube image load todo-frontend:v1.0.0
minikube image load todo-backend:v1.0.0

# Deploy with Helm
helm install todo-chatbot ./helm/todo-chatbot
```

### Deployment Order

**Decision**: Helm manages deployment order automatically

**Rationale**:
- Kubernetes handles dependency resolution
- Services can be created before pods (no issue)
- Pods will wait for required resources (Secrets, ConfigMaps)
- No explicit ordering needed for this simple deployment

**Validation Strategy**:
- Use `kubectl wait` for pod readiness
- Check service endpoints before accessing
- Verify frontend-to-backend connectivity
- Test end-to-end application functionality

## AI DevOps Tools Integration Research

### Gordon (Docker AI)

**Capabilities**:
- Generate Dockerfiles from natural language prompts
- Optimize existing Dockerfiles
- Suggest best practices and security improvements

**Usage Pattern**:
```
Prompt: "Create a production-ready multi-stage Dockerfile for a Next.js 16
application with App Router. Use Node 18 Alpine base image, install dependencies,
build the application, and create a minimal runtime image."
```

**Validation**:
- Review generated Dockerfile for correctness
- Test build locally
- Verify image size and functionality
- Document any manual modifications

**Fallback**: Manual Dockerfile creation using documented best practices

### kubectl-ai

**Capabilities**:
- Generate Kubernetes manifests from descriptions
- Debug deployment issues with natural language queries
- Suggest fixes for common problems

**Usage Pattern**:
```
Prompt: "Create a Kubernetes Deployment for a Next.js frontend application
with 1 replica, resource limits of 512Mi memory and 500m CPU, health checks
on port 3000, and environment variable for API_BASE_URL."
```

**Validation**:
- Review generated YAML for correctness
- Apply to test cluster
- Verify pod behavior
- Integrate into Helm templates

**Fallback**: Manual kubectl commands and manifest creation

### kagent

**Capabilities**:
- Analyze cluster state and resource utilization
- Identify performance bottlenecks
- Suggest optimization opportunities

**Usage Pattern**:
```
Prompt: "Analyze the todo-chatbot deployment and identify any resource
constraints, networking issues, or performance bottlenecks."
```

**Validation**:
- Cross-reference with kubectl commands
- Verify recommendations
- Implement suggested improvements

**Fallback**: Manual kubectl analysis (get, describe, logs, top)

## Configuration Management Research

### Decision: Externalized Configuration Pattern

**Rationale**:
- Follows 12-factor app principles
- Enables environment-specific configuration
- Separates secrets from code
- Supports configuration changes without rebuilds

**Implementation**:
- Helm values.yaml: Default configuration
- Kubernetes Secrets: Sensitive data (base64 encoded)
- Kubernetes ConfigMaps: Non-sensitive configuration
- Environment variables: Injected into containers

**Security Considerations**:
- Never commit secrets to version control
- Use base64 encoding for Secrets (Kubernetes requirement)
- Consider external secret management for production (out of scope for Phase IV)
- Rotate secrets regularly (manual process for Phase IV)

## Performance Optimization Research

### Image Size Optimization

**Techniques Applied**:
- Multi-stage builds (reduces size by 60-70%)
- Alpine base images (minimal footprint)
- .dockerignore files (exclude unnecessary files)
- Layer caching (faster rebuilds)

**Expected Results**:
- Frontend image: ~150-200MB (vs 500MB+ single-stage)
- Backend image: ~200-250MB (vs 800MB+ single-stage)

### Deployment Speed Optimization

**Techniques Applied**:
- Local image loading (no registry pull time)
- Readiness probes (traffic only to ready pods)
- Resource limits (prevent resource contention)
- Efficient Helm templates (fast rendering)

**Expected Results**:
- Helm install: < 5 minutes
- Pods Running: < 5 minutes
- Frontend accessible: < 1 minute after pods ready

## Risk Mitigation Strategies

### Risk: Docker Build Failures

**Mitigation**:
- Test builds locally before Minikube deployment
- Use proven base images
- Pin dependency versions
- Implement build validation in tasks

### Risk: Pod Startup Failures

**Mitigation**:
- Validate Secrets and ConfigMaps before deployment
- Use init containers if dependencies required
- Implement proper health checks
- Set appropriate resource limits

### Risk: Service Communication Failures

**Mitigation**:
- Use Kubernetes DNS for service discovery
- Verify network policies (none expected in Minikube)
- Test connectivity with temporary pods
- Check service endpoints

### Risk: AI Tool Unavailability

**Mitigation**:
- Document manual fallback processes
- Provide example Dockerfiles and manifests
- Include troubleshooting guides
- Validate all AI-generated artifacts

## Conclusion

All research findings support the architectural decisions outlined in plan.md. The deployment strategy balances simplicity (appropriate for local development) with best practices (production-ready patterns). AI DevOps tools will accelerate development but are not critical dependencies - manual fallbacks are documented and tested.

**Ready for Phase 1**: Design & Contracts

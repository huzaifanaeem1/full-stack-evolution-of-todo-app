# Helm Values Schema: Todo Chatbot Deployment

**Feature**: 003-minikube-deployment
**Date**: 2026-02-08
**Purpose**: Define the structure and schema for Helm chart values.yaml

## Overview

This document defines the complete schema for the `values.yaml` file used to configure the Todo Chatbot Helm chart. All values are configurable and have sensible defaults for local Minikube deployment.

## Global Configuration

```yaml
global:
  # Kubernetes namespace for all resources
  namespace: default

  # Common labels applied to all resources
  labels:
    app: todo-chatbot
    environment: development
    managed-by: helm
```

**Description**:
- `namespace`: Target namespace for deployment (default: `default`)
- `labels`: Common labels applied to all Kubernetes resources

---

## Frontend Configuration

```yaml
frontend:
  # Docker image configuration
  image:
    repository: todo-frontend
    tag: v1.0.0
    pullPolicy: IfNotPresent

  # Number of pod replicas
  replicas: 1

  # Resource limits and requests
  resources:
    limits:
      memory: "512Mi"
      cpu: "500m"
    requests:
      memory: "256Mi"
      cpu: "250m"

  # Service configuration
  service:
    type: NodePort
    port: 3000
    targetPort: 3000
    # nodePort: 30080  # Optional: specify NodePort (30000-32767)

  # Health check configuration
  livenessProbe:
    httpGet:
      path: /
      port: 3000
    initialDelaySeconds: 10
    periodSeconds: 10
    timeoutSeconds: 5
    failureThreshold: 3

  readinessProbe:
    httpGet:
      path: /
      port: 3000
    initialDelaySeconds: 10
    periodSeconds: 10
    timeoutSeconds: 5
    failureThreshold: 3

  # Environment variables
  env:
    ENVIRONMENT: development
    # NEXT_PUBLIC_API_BASE_URL will be set to backend service URL automatically
```

**Field Descriptions**:

- `image.repository`: Docker image name (default: `todo-frontend`)
- `image.tag`: Image version tag (default: `v1.0.0`)
- `image.pullPolicy`: Image pull policy (default: `IfNotPresent`)
- `replicas`: Number of frontend pods (default: `1`)
- `resources.limits`: Maximum resources per pod
- `resources.requests`: Requested resources per pod
- `service.type`: Kubernetes service type (default: `NodePort` for external access)
- `service.port`: Service port (default: `3000`)
- `service.targetPort`: Container port (default: `3000`)
- `livenessProbe`: Configuration for liveness health check
- `readinessProbe`: Configuration for readiness health check
- `env`: Additional environment variables

---

## Backend Configuration

```yaml
backend:
  # Docker image configuration
  image:
    repository: todo-backend
    tag: v1.0.0
    pullPolicy: IfNotPresent

  # Number of pod replicas
  replicas: 1

  # Resource limits and requests
  resources:
    limits:
      memory: "1Gi"
      cpu: "1000m"
    requests:
      memory: "512Mi"
      cpu: "500m"

  # Service configuration
  service:
    type: ClusterIP
    port: 8000
    targetPort: 8000

  # Health check configuration
  livenessProbe:
    httpGet:
      path: /health
      port: 8000
    initialDelaySeconds: 15
    periodSeconds: 10
    timeoutSeconds: 5
    failureThreshold: 3

  readinessProbe:
    httpGet:
      path: /health
      port: 8000
    initialDelaySeconds: 15
    periodSeconds: 10
    timeoutSeconds: 5
    failureThreshold: 3

  # Environment variables
  env:
    ENVIRONMENT: development
    # DATABASE_URL and JWT_SECRET will be injected from secrets
```

**Field Descriptions**:

- `image.repository`: Docker image name (default: `todo-backend`)
- `image.tag`: Image version tag (default: `v1.0.0`)
- `image.pullPolicy`: Image pull policy (default: `IfNotPresent`)
- `replicas`: Number of backend pods (default: `1`)
- `resources.limits`: Maximum resources per pod
- `resources.requests`: Requested resources per pod
- `service.type`: Kubernetes service type (default: `ClusterIP` for internal only)
- `service.port`: Service port (default: `8000`)
- `service.targetPort`: Container port (default: `8000`)
- `livenessProbe`: Configuration for liveness health check
- `readinessProbe`: Configuration for readiness health check
- `env`: Additional environment variables

---

## Secrets Configuration

```yaml
secrets:
  # Database connection string (base64 encoded)
  # Example: postgresql://user:password@host:5432/dbname
  databaseUrl: ""

  # JWT signing secret (base64 encoded)
  # Example: your-super-secret-jwt-key-here
  jwtSecret: ""
```

**Field Descriptions**:

- `databaseUrl`: PostgreSQL connection string (must be base64 encoded)
- `jwtSecret`: JWT signing secret (must be base64 encoded)

**Important**: These values must be provided during Helm installation and should be base64 encoded.

**Encoding Example**:
```bash
echo -n "postgresql://user:password@host:5432/dbname" | base64
echo -n "your-super-secret-jwt-key" | base64
```

---

## ConfigMap Configuration

```yaml
configMap:
  # Non-sensitive application configuration
  data:
    ENVIRONMENT: development
    # Additional configuration key-value pairs
```

**Field Descriptions**:

- `data`: Key-value pairs for non-sensitive configuration
- Values are injected as environment variables into pods

---

## Complete Example values.yaml

```yaml
global:
  namespace: default
  labels:
    app: todo-chatbot
    environment: development
    managed-by: helm

frontend:
  image:
    repository: todo-frontend
    tag: v1.0.0
    pullPolicy: IfNotPresent
  replicas: 1
  resources:
    limits:
      memory: "512Mi"
      cpu: "500m"
    requests:
      memory: "256Mi"
      cpu: "250m"
  service:
    type: NodePort
    port: 3000
    targetPort: 3000
  livenessProbe:
    httpGet:
      path: /
      port: 3000
    initialDelaySeconds: 10
    periodSeconds: 10
    timeoutSeconds: 5
    failureThreshold: 3
  readinessProbe:
    httpGet:
      path: /
      port: 3000
    initialDelaySeconds: 10
    periodSeconds: 10
    timeoutSeconds: 5
    failureThreshold: 3
  env:
    ENVIRONMENT: development

backend:
  image:
    repository: todo-backend
    tag: v1.0.0
    pullPolicy: IfNotPresent
  replicas: 1
  resources:
    limits:
      memory: "1Gi"
      cpu: "1000m"
    requests:
      memory: "512Mi"
      cpu: "500m"
  service:
    type: ClusterIP
    port: 8000
    targetPort: 8000
  livenessProbe:
    httpGet:
      path: /health
      port: 8000
    initialDelaySeconds: 15
    periodSeconds: 10
    timeoutSeconds: 5
    failureThreshold: 3
  readinessProbe:
    httpGet:
      path: /health
      port: 8000
    initialDelaySeconds: 15
    periodSeconds: 10
    timeoutSeconds: 5
    failureThreshold: 3
  env:
    ENVIRONMENT: development

secrets:
  # MUST be base64 encoded
  databaseUrl: "cG9zdGdyZXNxbDovL3VzZXI6cGFzc3dvcmRAaG9zdDo1NDMyL2RibmFtZQ=="
  jwtSecret: "eW91ci1zdXBlci1zZWNyZXQtand0LWtleS1oZXJl"

configMap:
  data:
    ENVIRONMENT: development
```

## Validation Rules

**Required Fields**:
- `secrets.databaseUrl`: Must be provided and base64 encoded
- `secrets.jwtSecret`: Must be provided and base64 encoded

**Optional Fields**:
- All other fields have sensible defaults

**Constraints**:
- `replicas`: Must be >= 1
- `resources.limits.memory`: Must be >= resources.requests.memory
- `resources.limits.cpu`: Must be >= resources.requests.cpu
- `service.port`: Must be valid port number (1-65535)
- `service.nodePort`: If specified, must be in range 30000-32767

## Usage Examples

### Minimal Installation (using defaults)

```bash
helm install todo-chatbot ./helm/todo-chatbot \
  --set secrets.databaseUrl="$(echo -n 'postgresql://...' | base64)" \
  --set secrets.jwtSecret="$(echo -n 'secret-key' | base64)"
```

### Custom Configuration

```bash
helm install todo-chatbot ./helm/todo-chatbot \
  --set frontend.replicas=2 \
  --set backend.replicas=2 \
  --set frontend.image.tag=v1.1.0 \
  --set backend.image.tag=v1.1.0 \
  --set secrets.databaseUrl="$(echo -n 'postgresql://...' | base64)" \
  --set secrets.jwtSecret="$(echo -n 'secret-key' | base64)"
```

### Using Custom values.yaml

```bash
# Create custom-values.yaml with overrides
helm install todo-chatbot ./helm/todo-chatbot -f custom-values.yaml
```

## Upgrade Scenarios

### Update Image Tags

```bash
helm upgrade todo-chatbot ./helm/todo-chatbot \
  --set frontend.image.tag=v1.1.0 \
  --set backend.image.tag=v1.1.0 \
  --reuse-values
```

### Scale Replicas

```bash
helm upgrade todo-chatbot ./helm/todo-chatbot \
  --set frontend.replicas=3 \
  --set backend.replicas=3 \
  --reuse-values
```

### Update Secrets

```bash
helm upgrade todo-chatbot ./helm/todo-chatbot \
  --set secrets.jwtSecret="$(echo -n 'new-secret-key' | base64)" \
  --reuse-values
```

## Rollback

```bash
# Rollback to previous release
helm rollback todo-chatbot

# Rollback to specific revision
helm rollback todo-chatbot 2
```

## Uninstall

```bash
helm uninstall todo-chatbot
```

This removes all Kubernetes resources created by the chart.

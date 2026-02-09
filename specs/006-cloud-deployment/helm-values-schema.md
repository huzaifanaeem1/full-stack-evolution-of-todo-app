# Helm Values Schema Documentation

**Feature**: 006-cloud-deployment
**Date**: 2026-02-09
**Purpose**: Document all configurable values in Helm charts with types, defaults, and descriptions

---

## Table of Contents

1. [Global Values](#global-values)
2. [Frontend Values](#frontend-values)
3. [Backend Values](#backend-values)
4. [Recurring Task Service Values](#recurring-task-service-values)
5. [Notification Service Values](#notification-service-values)
6. [Kafka Values](#kafka-values)
7. [Dapr Components Values](#dapr-components-values)
8. [Environment-Specific Overrides](#environment-specific-overrides)

---

## Global Values

Global values are shared across all subcharts in the umbrella chart. They can be overridden by individual chart values.

### Namespace Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `global.namespace` | string | `"todo-app"` | Kubernetes namespace for all resources |

### Image Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `global.imageRegistry` | string | `"docker.io"` | Container registry for all images |
| `global.imageTag` | string | `"latest"` | Default image tag for all services |
| `global.imagePullPolicy` | string | `"IfNotPresent"` | Image pull policy (Always, IfNotPresent, Never) |
| `global.imagePullSecrets` | list | `[]` | Image pull secrets for private registries |

### Secrets Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `global.secrets.databaseUrl` | string | `""` | PostgreSQL connection string (required) |
| `global.secrets.jwtSecret` | string | `""` | JWT secret for authentication (required) |

**Example**:
```yaml
global:
  namespace: todo-app
  imageRegistry: docker.io
  imageTag: v1.0.0
  imagePullPolicy: IfNotPresent
  secrets:
    databaseUrl: "postgresql://user:pass@host:5432/db"
    jwtSecret: "your-secret-key"
```

---

## Frontend Values

Configuration for the Next.js frontend service.

### Image Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `frontend.image.repository` | string | `"frontend"` | Image repository name |
| `frontend.image.tag` | string | `global.imageTag` | Image tag (overrides global) |
| `frontend.image.pullPolicy` | string | `global.imagePullPolicy` | Image pull policy (overrides global) |

### Deployment Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `frontend.replicaCount` | integer | `2` | Number of pod replicas |
| `frontend.revisionHistoryLimit` | integer | `3` | Number of old ReplicaSets to retain |

### Resource Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `frontend.resources.requests.cpu` | string | `"100m"` | CPU request (0.1 cores) |
| `frontend.resources.requests.memory` | string | `"128Mi"` | Memory request (128 MiB) |
| `frontend.resources.limits.cpu` | string | `"500m"` | CPU limit (0.5 cores) |
| `frontend.resources.limits.memory` | string | `"512Mi"` | Memory limit (512 MiB) |

### Service Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `frontend.service.type` | string | `"LoadBalancer"` | Service type (LoadBalancer, ClusterIP, NodePort) |
| `frontend.service.port` | integer | `80` | Service port |
| `frontend.service.targetPort` | integer | `3000` | Container port |
| `frontend.service.annotations` | object | `{}` | Service annotations (cloud-specific) |

### Ingress Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `frontend.ingress.enabled` | boolean | `false` | Enable Ingress resource |
| `frontend.ingress.className` | string | `"nginx"` | Ingress class name |
| `frontend.ingress.annotations` | object | `{}` | Ingress annotations |
| `frontend.ingress.hosts` | list | `[]` | Ingress host rules |
| `frontend.ingress.tls` | list | `[]` | TLS configuration |

### Health Checks

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `frontend.livenessProbe.httpGet.path` | string | `"/"` | Liveness probe path |
| `frontend.livenessProbe.httpGet.port` | integer | `3000` | Liveness probe port |
| `frontend.livenessProbe.initialDelaySeconds` | integer | `30` | Initial delay before probing |
| `frontend.livenessProbe.periodSeconds` | integer | `10` | Probe frequency |
| `frontend.livenessProbe.timeoutSeconds` | integer | `5` | Probe timeout |
| `frontend.livenessProbe.failureThreshold` | integer | `3` | Failures before restart |
| `frontend.readinessProbe.httpGet.path` | string | `"/"` | Readiness probe path |
| `frontend.readinessProbe.httpGet.port` | integer | `3000` | Readiness probe port |
| `frontend.readinessProbe.initialDelaySeconds` | integer | `10` | Initial delay before probing |
| `frontend.readinessProbe.periodSeconds` | integer | `5` | Probe frequency |
| `frontend.readinessProbe.timeoutSeconds` | integer | `3` | Probe timeout |
| `frontend.readinessProbe.failureThreshold` | integer | `3` | Failures before marking unready |

**Example**:
```yaml
frontend:
  replicaCount: 2
  image:
    repository: myregistry/frontend
    tag: v1.0.0
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 512Mi
  service:
    type: LoadBalancer
    port: 80
```

---

## Backend Values

Configuration for the FastAPI backend (Chat API) service.

### Image Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `backend.image.repository` | string | `"backend"` | Image repository name |
| `backend.image.tag` | string | `global.imageTag` | Image tag (overrides global) |
| `backend.image.pullPolicy` | string | `global.imagePullPolicy` | Image pull policy (overrides global) |

### Deployment Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `backend.replicaCount` | integer | `2` | Number of pod replicas |
| `backend.revisionHistoryLimit` | integer | `3` | Number of old ReplicaSets to retain |

### Dapr Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `backend.dapr.enabled` | boolean | `true` | Enable Dapr sidecar injection |
| `backend.dapr.appId` | string | `"backend"` | Dapr application ID |
| `backend.dapr.appPort` | integer | `8000` | Application port for Dapr |
| `backend.dapr.logLevel` | string | `"info"` | Dapr log level (debug, info, warn, error) |

### Resource Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `backend.resources.requests.cpu` | string | `"200m"` | CPU request (0.2 cores) |
| `backend.resources.requests.memory` | string | `"256Mi"` | Memory request (256 MiB) |
| `backend.resources.limits.cpu` | string | `"1000m"` | CPU limit (1 core) |
| `backend.resources.limits.memory` | string | `"1Gi"` | Memory limit (1 GiB) |

### Service Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `backend.service.type` | string | `"ClusterIP"` | Service type (internal only) |
| `backend.service.port` | integer | `8000` | Service port |
| `backend.service.targetPort` | integer | `8000` | Container port |

### Environment Variables

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `backend.env.DATABASE_URL` | string | `global.secrets.databaseUrl` | Database connection string (from secret) |
| `backend.env.JWT_SECRET` | string | `global.secrets.jwtSecret` | JWT secret (from secret) |
| `backend.env.LOG_LEVEL` | string | `"INFO"` | Application log level |

### Health Checks

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `backend.livenessProbe.httpGet.path` | string | `"/health"` | Liveness probe path |
| `backend.livenessProbe.httpGet.port` | integer | `8000` | Liveness probe port |
| `backend.livenessProbe.initialDelaySeconds` | integer | `30` | Initial delay before probing |
| `backend.livenessProbe.periodSeconds` | integer | `10` | Probe frequency |
| `backend.livenessProbe.timeoutSeconds` | integer | `5` | Probe timeout |
| `backend.livenessProbe.failureThreshold` | integer | `3` | Failures before restart |
| `backend.readinessProbe.httpGet.path` | string | `"/health"` | Readiness probe path |
| `backend.readinessProbe.httpGet.port` | integer | `8000` | Readiness probe port |
| `backend.readinessProbe.initialDelaySeconds` | integer | `10` | Initial delay before probing |
| `backend.readinessProbe.periodSeconds` | integer | `5` | Probe frequency |
| `backend.readinessProbe.timeoutSeconds` | integer | `3` | Probe timeout |
| `backend.readinessProbe.failureThreshold` | integer | `3` | Failures before marking unready |

**Example**:
```yaml
backend:
  replicaCount: 2
  dapr:
    enabled: true
    appId: backend
    appPort: 8000
    logLevel: info
  resources:
    requests:
      cpu: 200m
      memory: 256Mi
    limits:
      cpu: 1000m
      memory: 1Gi
```

---

## Recurring Task Service Values

Configuration for the Recurring Task Service.

### Image Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `recurringTaskService.image.repository` | string | `"recurring-task-service"` | Image repository name |
| `recurringTaskService.image.tag` | string | `global.imageTag` | Image tag (overrides global) |
| `recurringTaskService.image.pullPolicy` | string | `global.imagePullPolicy` | Image pull policy (overrides global) |

### Deployment Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `recurringTaskService.replicaCount` | integer | `1` | Number of pod replicas |
| `recurringTaskService.revisionHistoryLimit` | integer | `3` | Number of old ReplicaSets to retain |

### Dapr Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `recurringTaskService.dapr.enabled` | boolean | `true` | Enable Dapr sidecar injection |
| `recurringTaskService.dapr.appId` | string | `"recurring-task-service"` | Dapr application ID |
| `recurringTaskService.dapr.appPort` | integer | `8001` | Application port for Dapr |
| `recurringTaskService.dapr.logLevel` | string | `"info"` | Dapr log level |

### Resource Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `recurringTaskService.resources.requests.cpu` | string | `"100m"` | CPU request (0.1 cores) |
| `recurringTaskService.resources.requests.memory` | string | `"128Mi"` | Memory request (128 MiB) |
| `recurringTaskService.resources.limits.cpu` | string | `"500m"` | CPU limit (0.5 cores) |
| `recurringTaskService.resources.limits.memory` | string | `"512Mi"` | Memory limit (512 MiB) |

### Service Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `recurringTaskService.service.type` | string | `"ClusterIP"` | Service type (internal only) |
| `recurringTaskService.service.port` | integer | `8001` | Service port |
| `recurringTaskService.service.targetPort` | integer | `8001` | Container port |

### Environment Variables

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `recurringTaskService.env.DATABASE_URL` | string | `global.secrets.databaseUrl` | Database connection string (from secret) |
| `recurringTaskService.env.LOG_LEVEL` | string | `"INFO"` | Application log level |

**Example**:
```yaml
recurringTaskService:
  replicaCount: 1
  dapr:
    enabled: true
    appId: recurring-task-service
    appPort: 8001
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
```

---

## Notification Service Values

Configuration for the Notification Service.

### Image Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `notificationService.image.repository` | string | `"notification-service"` | Image repository name |
| `notificationService.image.tag` | string | `global.imageTag` | Image tag (overrides global) |
| `notificationService.image.pullPolicy` | string | `global.imagePullPolicy` | Image pull policy (overrides global) |

### Deployment Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `notificationService.replicaCount` | integer | `1` | Number of pod replicas |
| `notificationService.revisionHistoryLimit` | integer | `3` | Number of old ReplicaSets to retain |

### Dapr Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `notificationService.dapr.enabled` | boolean | `true` | Enable Dapr sidecar injection |
| `notificationService.dapr.appId` | string | `"notification-service"` | Dapr application ID |
| `notificationService.dapr.appPort` | integer | `8002` | Application port for Dapr |
| `notificationService.dapr.logLevel` | string | `"info"` | Dapr log level |

### Resource Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `notificationService.resources.requests.cpu` | string | `"50m"` | CPU request (0.05 cores) |
| `notificationService.resources.requests.memory` | string | `"64Mi"` | Memory request (64 MiB) |
| `notificationService.resources.limits.cpu` | string | `"200m"` | CPU limit (0.2 cores) |
| `notificationService.resources.limits.memory` | string | `"256Mi"` | Memory limit (256 MiB) |

### Service Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `notificationService.service.type` | string | `"ClusterIP"` | Service type (internal only) |
| `notificationService.service.port` | integer | `8002` | Service port |
| `notificationService.service.targetPort` | integer | `8002` | Container port |

**Example**:
```yaml
notificationService:
  replicaCount: 1
  dapr:
    enabled: true
    appId: notification-service
    appPort: 8002
  resources:
    requests:
      cpu: 50m
      memory: 64Mi
```

---

## Kafka Values

Configuration for Kafka and Zookeeper.

### Kafka Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `kafka.replicaCount` | integer | `1` | Number of Kafka broker replicas |
| `kafka.image.repository` | string | `"confluentinc/cp-kafka"` | Kafka image repository |
| `kafka.image.tag` | string | `"7.5.0"` | Kafka image tag |
| `kafka.image.pullPolicy` | string | `"IfNotPresent"` | Image pull policy |

### Kafka Resource Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `kafka.resources.requests.cpu` | string | `"500m"` | CPU request (0.5 cores) |
| `kafka.resources.requests.memory` | string | `"1Gi"` | Memory request (1 GiB) |
| `kafka.resources.limits.cpu` | string | `"2000m"` | CPU limit (2 cores) |
| `kafka.resources.limits.memory` | string | `"4Gi"` | Memory limit (4 GiB) |

### Kafka Storage Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `kafka.persistence.enabled` | boolean | `true` | Enable persistent storage |
| `kafka.persistence.storageClass` | string | `""` | Storage class (empty = default) |
| `kafka.persistence.size` | string | `"10Gi"` | PersistentVolume size |
| `kafka.persistence.accessMode` | string | `"ReadWriteOnce"` | Access mode |

### Kafka Service Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `kafka.service.type` | string | `"ClusterIP"` | Service type (internal only) |
| `kafka.service.port` | integer | `9092` | Kafka broker port |

### Zookeeper Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `zookeeper.replicaCount` | integer | `1` | Number of Zookeeper replicas |
| `zookeeper.image.repository` | string | `"confluentinc/cp-zookeeper"` | Zookeeper image repository |
| `zookeeper.image.tag` | string | `"7.5.0"` | Zookeeper image tag |
| `zookeeper.image.pullPolicy` | string | `"IfNotPresent"` | Image pull policy |

### Zookeeper Resource Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `zookeeper.resources.requests.cpu` | string | `"250m"` | CPU request (0.25 cores) |
| `zookeeper.resources.requests.memory` | string | `"512Mi"` | Memory request (512 MiB) |
| `zookeeper.resources.limits.cpu` | string | `"1000m"` | CPU limit (1 core) |
| `zookeeper.resources.limits.memory` | string | `"2Gi"` | Memory limit (2 GiB) |

### Zookeeper Storage Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `zookeeper.persistence.enabled` | boolean | `true` | Enable persistent storage |
| `zookeeper.persistence.storageClass` | string | `""` | Storage class (empty = default) |
| `zookeeper.persistence.size` | string | `"5Gi"` | PersistentVolume size |
| `zookeeper.persistence.accessMode` | string | `"ReadWriteOnce"` | Access mode |

**Example**:
```yaml
kafka:
  replicaCount: 1
  resources:
    requests:
      cpu: 500m
      memory: 1Gi
    limits:
      cpu: 2000m
      memory: 4Gi
  persistence:
    enabled: true
    size: 10Gi

zookeeper:
  replicaCount: 1
  resources:
    requests:
      cpu: 250m
      memory: 512Mi
  persistence:
    enabled: true
    size: 5Gi
```

---

## Dapr Components Values

Configuration for Dapr Pub/Sub and other components.

### Pub/Sub Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `daprComponents.pubsub.enabled` | boolean | `true` | Enable Pub/Sub component |
| `daprComponents.pubsub.name` | string | `"pubsub-kafka"` | Component name |
| `daprComponents.pubsub.type` | string | `"pubsub.kafka"` | Component type |
| `daprComponents.pubsub.version` | string | `"v1"` | Component version |
| `daprComponents.pubsub.metadata.brokers` | string | `"kafka:9092"` | Kafka broker addresses |
| `daprComponents.pubsub.metadata.consumerGroup` | string | `"dapr-consumer-group"` | Kafka consumer group |
| `daprComponents.pubsub.metadata.authType` | string | `"none"` | Authentication type |

### State Store Configuration (Optional)

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `daprComponents.statestore.enabled` | boolean | `false` | Enable State Store component |
| `daprComponents.statestore.name` | string | `"statestore"` | Component name |
| `daprComponents.statestore.type` | string | `"state.redis"` | Component type |
| `daprComponents.statestore.version` | string | `"v1"` | Component version |

**Example**:
```yaml
daprComponents:
  pubsub:
    enabled: true
    name: pubsub-kafka
    metadata:
      brokers: "kafka:9092"
      consumerGroup: "dapr-consumer-group"
```

---

## Environment-Specific Overrides

### Development Environment (values-dev.yaml)

```yaml
global:
  imageTag: dev
  imagePullPolicy: Always

frontend:
  replicaCount: 1
  service:
    type: NodePort

backend:
  replicaCount: 1
  dapr:
    logLevel: debug

kafka:
  persistence:
    size: 5Gi

zookeeper:
  persistence:
    size: 2Gi
```

### Staging Environment (values-staging.yaml)

```yaml
global:
  imageTag: staging
  imagePullPolicy: IfNotPresent

frontend:
  replicaCount: 2
  resources:
    requests:
      cpu: 150m
      memory: 192Mi

backend:
  replicaCount: 2
  resources:
    requests:
      cpu: 300m
      memory: 384Mi

kafka:
  persistence:
    size: 20Gi
```

### Production Environment (values-prod.yaml)

```yaml
global:
  imageTag: v1.0.0
  imagePullPolicy: IfNotPresent

frontend:
  replicaCount: 3
  resources:
    requests:
      cpu: 200m
      memory: 256Mi
    limits:
      cpu: 1000m
      memory: 1Gi

backend:
  replicaCount: 3
  resources:
    requests:
      cpu: 500m
      memory: 512Mi
    limits:
      cpu: 2000m
      memory: 2Gi

kafka:
  replicaCount: 3
  persistence:
    size: 50Gi

zookeeper:
  replicaCount: 3
  persistence:
    size: 10Gi
```

---

## Usage Examples

### Deploy with Default Values (Minikube)

```bash
helm install todo-app ./helm/todo-app \
  --namespace=todo-app \
  --create-namespace
```

### Deploy to Development Environment

```bash
helm install todo-app ./helm/todo-app \
  --namespace=todo-app \
  --values=./helm/todo-app/values-dev.yaml \
  --set global.secrets.databaseUrl="postgresql://..." \
  --set global.secrets.jwtSecret="dev-secret"
```

### Deploy to Production Environment

```bash
helm install todo-app ./helm/todo-app \
  --namespace=todo-app \
  --values=./helm/todo-app/values-prod.yaml \
  --set global.imageTag=v1.0.0 \
  --set global.secrets.databaseUrl="postgresql://..." \
  --set global.secrets.jwtSecret="prod-secret"
```

### Override Specific Values

```bash
helm install todo-app ./helm/todo-app \
  --namespace=todo-app \
  --set frontend.replicaCount=5 \
  --set backend.resources.limits.cpu=2000m \
  --set kafka.persistence.size=100Gi
```

---

## Validation

### Validate Values Schema

```bash
# Lint Helm chart
helm lint ./helm/todo-app

# Render templates with values
helm template todo-app ./helm/todo-app \
  --values=./helm/todo-app/values-prod.yaml \
  --set global.secrets.databaseUrl="test" \
  --set global.secrets.jwtSecret="test"

# Dry-run installation
helm install todo-app ./helm/todo-app \
  --namespace=todo-app \
  --dry-run --debug
```

---

## Notes

- All secret values should be provided via `--set` flags or external secret management, never committed to values files
- Resource requests and limits should be adjusted based on actual workload requirements
- Replica counts should be increased for production high availability
- Storage sizes should be monitored and increased as data grows
- Dapr log level should be `info` or `warn` in production to reduce log volume

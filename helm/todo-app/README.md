# Todo App Helm Chart

Complete Helm chart for deploying the Todo Application to Kubernetes with event-driven architecture.

## Overview

This umbrella chart deploys the complete Todo Application stack including:

- **Frontend** - Next.js web application (LoadBalancer)
- **Backend** - FastAPI REST API with Dapr sidecar (ClusterIP)
- **Kafka** - Message broker for event streaming
- **Zookeeper** - Kafka coordination service
- **Dapr Components** - Pub/Sub and State Store components
- **Recurring Task Service** - Automated task recurrence with Dapr
- **Notification Service** - Event-driven notifications with Dapr

## Prerequisites

- Kubernetes cluster (Minikube, Oracle Cloud, Azure AKS, Google GKE, etc.)
- `kubectl` CLI installed and configured
- `helm` 3.x installed
- `dapr` CLI installed (for Dapr control plane installation)
- PostgreSQL database (Neon Serverless or self-hosted)

## Quick Start

### 1. Install Dapr Control Plane

```bash
./scripts/install-dapr.sh dapr-system
```

### 2. Create Kubernetes Secrets

```bash
./scripts/create-secrets.sh todo-app \
  'postgresql://user:pass@host:5432/db' \
  'your-jwt-secret'
```

### 3. Deploy Full Stack

```bash
# Development environment
helm install todo-app ./helm/todo-app \
  --namespace todo-app \
  --create-namespace \
  --values ./helm/todo-app/values-dev.yaml

# Production environment
helm install todo-app ./helm/todo-app \
  --namespace todo-app \
  --create-namespace \
  --values ./helm/todo-app/values-prod.yaml
```

### 4. Verify Deployment

```bash
./scripts/validate-deployment.sh todo-app
```

## Automated Deployment

Use the master deployment script for automated full-stack deployment:

```bash
./scripts/deploy-to-cloud.sh todo-app prod \
  'postgresql://user:pass@host:5432/db' \
  'your-jwt-secret'
```

This script handles:
- Namespace creation
- Secret management
- Dapr installation
- Helm dependency updates
- Service deployment in correct order
- Validation checkpoints

## Environment-Specific Deployment

### Development (Minikube/Local)

```bash
helm install todo-app ./helm/todo-app \
  --namespace todo-app \
  --create-namespace \
  --values ./helm/todo-app/values-dev.yaml
```

**Configuration:**
- 1 replica per service
- Lower resource limits
- NodePort for frontend access

### Staging

```bash
helm install todo-app ./helm/todo-app \
  --namespace todo-app \
  --create-namespace \
  --values ./helm/todo-app/values-staging.yaml
```

**Configuration:**
- 2 replicas for critical services
- Medium resource limits
- LoadBalancer for frontend access

### Production

```bash
helm install todo-app ./helm/todo-app \
  --namespace todo-app \
  --create-namespace \
  --values ./helm/todo-app/values-prod.yaml
```

**Configuration:**
- 3 replicas for high availability
- High resource limits
- LoadBalancer for frontend access
- Kafka cluster with 3 brokers

## Partial Deployment

Deploy individual services by disabling others:

### Core Services Only (Frontend + Backend)

```bash
helm install todo-app ./helm/todo-app \
  --namespace todo-app \
  --set kafka.enabled=false \
  --set daprComponents.enabled=false \
  --set recurringTaskService.enabled=false \
  --set notificationService.enabled=false
```

### Event Services Only (Kafka + Dapr + Event Services)

```bash
# Assumes core services already deployed
helm install event-services ./helm/todo-app \
  --namespace todo-app \
  --set frontend.enabled=false \
  --set backend.enabled=false
```

## Upgrading

### Upgrade All Services

```bash
helm upgrade todo-app ./helm/todo-app \
  --namespace todo-app \
  --values ./helm/todo-app/values-prod.yaml
```

### Upgrade Individual Service

```bash
# Upgrade frontend only
helm upgrade frontend ./helm/frontend \
  --namespace todo-app \
  --values ./helm/todo-app/values-prod.yaml
```

## Rollback

### Rollback to Previous Version

```bash
./scripts/rollback.sh todo-app todo-app
```

### Rollback to Specific Revision

```bash
./scripts/rollback.sh todo-app todo-app 5
```

### View Release History

```bash
helm history todo-app -n todo-app
```

## Configuration

### Required Values

Set these values via `--set` or in values files:

```yaml
global:
  secrets:
    databaseUrl: "postgresql://user:pass@host:5432/db"
    jwtSecret: "your-jwt-secret"
```

### Common Overrides

```bash
# Change replica count
--set frontend.replicaCount=3

# Change image tag
--set global.imageTag=v1.2.3

# Change service type
--set frontend.service.type=NodePort

# Disable Kafka persistence
--set kafka.persistence.enabled=false
```

## Accessing the Application

### LoadBalancer (Cloud)

```bash
kubectl get svc frontend -n todo-app
# Access via EXTERNAL-IP
```

### NodePort (Minikube)

```bash
minikube service frontend -n todo-app
```

### Port Forward (Development)

```bash
kubectl port-forward svc/frontend 3000:80 -n todo-app
# Access at http://localhost:3000
```

## Monitoring

### View Pods

```bash
kubectl get pods -n todo-app
```

### View Logs

```bash
# Frontend logs
kubectl logs -f deployment/frontend -n todo-app

# Backend logs (app container)
kubectl logs -f deployment/backend -n todo-app

# Backend logs (Dapr sidecar)
kubectl logs -f deployment/backend -c daprd -n todo-app

# Kafka logs
kubectl logs -f statefulset/kafka -n todo-app
```

### View Dapr Components

```bash
kubectl get components -n todo-app
```

### Check Dapr Status

```bash
dapr status -k
```

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n todo-app

# Check events
kubectl get events -n todo-app --sort-by='.lastTimestamp'
```

### Secrets Not Found

```bash
# Verify secrets exist
kubectl get secret app-secrets -n todo-app

# Recreate secrets
./scripts/create-secrets.sh todo-app '<db-url>' '<jwt-secret>'
```

### Dapr Sidecar Issues

```bash
# Check Dapr control plane
kubectl get pods -n dapr-system

# Reinstall Dapr
./scripts/install-dapr.sh dapr-system
```

### LoadBalancer Pending

```bash
# Check service status
kubectl get svc frontend -n todo-app

# For Minikube, use NodePort instead
helm upgrade todo-app ./helm/todo-app \
  --set frontend.service.type=NodePort \
  --namespace todo-app
```

## Uninstalling

### Uninstall Application

```bash
helm uninstall todo-app -n todo-app
```

### Delete Namespace

```bash
kubectl delete namespace todo-app
```

### Uninstall Dapr

```bash
helm uninstall dapr -n dapr-system
kubectl delete namespace dapr-system
```

## Chart Structure

```
helm/todo-app/
├── Chart.yaml              # Umbrella chart metadata
├── values.yaml             # Default values (dev)
├── values-dev.yaml         # Development overrides
├── values-staging.yaml     # Staging overrides
├── values-prod.yaml        # Production overrides
├── templates/
│   ├── namespace.yaml      # Namespace definition
│   ├── secrets.yaml        # Secret references
│   ├── configmap.yaml      # Shared configuration
│   ├── _helpers.tpl        # Template helpers
│   └── NOTES.txt           # Post-install notes
└── charts/                 # Subcharts (symlinked)
    ├── frontend/
    ├── backend/
    ├── kafka/
    ├── dapr-components/
    ├── recurring-task-service/
    └── notification-service/
```

## Documentation

- **Deployment Guide**: `specs/006-cloud-deployment/deployment-guide.md`
- **Helm Values Schema**: `specs/006-cloud-deployment/helm-values-schema.md`
- **Architecture Plan**: `specs/006-cloud-deployment/plan.md`
- **Feature Specification**: `specs/006-cloud-deployment/spec.md`

## Support

For issues and questions:
- Check the troubleshooting section in `deployment-guide.md`
- Review pod logs and events
- Verify all prerequisites are met
- Ensure secrets are correctly configured

## Version

Chart Version: 1.0.0
App Version: 1.0.0

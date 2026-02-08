# Kubernetes Resource Model: Local Kubernetes Deployment

**Feature**: 003-minikube-deployment
**Date**: 2026-02-08
**Purpose**: Define Kubernetes resources and their relationships for Todo Chatbot deployment

## Overview

This document describes the Kubernetes resources required for deploying the Todo Chatbot application on Minikube. The deployment consists of two primary services (frontend and backend) with supporting configuration resources.

## Resource Entities

### Frontend Deployment

**Type**: Kubernetes Deployment (apps/v1)

**Purpose**: Manages frontend application pods running the Next.js application

**Attributes**:
- Name: `todo-frontend`
- Namespace: `default` (configurable)
- Replicas: 1 (configurable via Helm values)
- Selector: `app: todo-frontend`
- Strategy: RollingUpdate (default)

**Container Specification**:
- Image: `todo-frontend:v1.0.0`
- Port: 3000
- Resource Limits: 512Mi memory, 500m CPU
- Resource Requests: 256Mi memory, 250m CPU

**Environment Variables**:
- `NEXT_PUBLIC_API_BASE_URL`: Backend service URL (from ConfigMap)
- `ENVIRONMENT`: Deployment environment (development/production)

**Health Checks**:
- Liveness Probe: HTTP GET / on port 3000
- Readiness Probe: HTTP GET / on port 3000
- Initial Delay: 10 seconds
- Period: 10 seconds
- Timeout: 5 seconds

**Relationships**:
- Managed by: Helm Chart
- Exposes: Port 3000 to Frontend Service
- Depends on: Backend Service (for API calls)
- Consumes: ConfigMap (for configuration)

---

### Backend Deployment

**Type**: Kubernetes Deployment (apps/v1)

**Purpose**: Manages backend application pods running the FastAPI application

**Attributes**:
- Name: `todo-backend`
- Namespace: `default` (configurable)
- Replicas: 1 (configurable via Helm values)
- Selector: `app: todo-backend`
- Strategy: RollingUpdate (default)

**Container Specification**:
- Image: `todo-backend:v1.0.0`
- Port: 8000
- Resource Limits: 1Gi memory, 1000m CPU
- Resource Requests: 512Mi memory, 500m CPU

**Environment Variables**:
- `DATABASE_URL`: PostgreSQL connection string (from Secret)
- `JWT_SECRET`: JWT signing secret (from Secret)
- `ENVIRONMENT`: Deployment environment (development/production)

**Health Checks**:
- Liveness Probe: HTTP GET /health on port 8000
- Readiness Probe: HTTP GET /health on port 8000
- Initial Delay: 15 seconds
- Period: 10 seconds
- Timeout: 5 seconds

**Relationships**:
- Managed by: Helm Chart
- Exposes: Port 8000 to Backend Service
- Depends on: Secrets (for DATABASE_URL, JWT_SECRET)
- Depends on: External Database (Neon PostgreSQL)
- Consumes: ConfigMap (for configuration)

---

### Frontend Service

**Type**: Kubernetes Service (v1)

**Purpose**: Exposes frontend pods for external access via Minikube

**Attributes**:
- Name: `todo-frontend-service`
- Namespace: `default` (configurable)
- Type: NodePort
- Selector: `app: todo-frontend`

**Port Configuration**:
- Port: 3000 (service port)
- TargetPort: 3000 (container port)
- NodePort: Auto-assigned by Kubernetes (30000-32767 range)

**Relationships**:
- Managed by: Helm Chart
- Selects: Frontend Deployment pods
- Accessed by: External users via Minikube service URL
- Routes traffic to: Frontend pods on port 3000

---

### Backend Service

**Type**: Kubernetes Service (v1)

**Purpose**: Exposes backend pods for internal cluster access

**Attributes**:
- Name: `todo-backend-service`
- Namespace: `default` (configurable)
- Type: ClusterIP (internal only)
- Selector: `app: todo-backend`

**Port Configuration**:
- Port: 8000 (service port)
- TargetPort: 8000 (container port)

**DNS Name**: `todo-backend-service.default.svc.cluster.local`

**Relationships**:
- Managed by: Helm Chart
- Selects: Backend Deployment pods
- Accessed by: Frontend pods via Kubernetes DNS
- Routes traffic to: Backend pods on port 8000

---

### ConfigMap

**Type**: Kubernetes ConfigMap (v1)

**Purpose**: Stores non-sensitive application configuration

**Attributes**:
- Name: `todo-chatbot-config`
- Namespace: `default` (configurable)

**Data**:
- `ENVIRONMENT`: Deployment environment (development/production)
- `API_BASE_URL`: Backend service URL for frontend
- Additional application-specific configuration

**Relationships**:
- Managed by: Helm Chart
- Consumed by: Frontend Deployment (as environment variables)
- Consumed by: Backend Deployment (as environment variables)

---

### Secrets

**Type**: Kubernetes Secret (v1)

**Purpose**: Stores sensitive configuration data

**Attributes**:
- Name: `todo-chatbot-secrets`
- Namespace: `default` (configurable)
- Type: Opaque

**Data** (base64 encoded):
- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET`: JWT signing secret

**Relationships**:
- Managed by: Helm Chart
- Consumed by: Backend Deployment (as environment variables)
- Values provided via: Helm values.yaml (base64 encoded)

---

### Helm Chart

**Type**: Helm Chart (v3)

**Purpose**: Packages and manages all Kubernetes resources as a cohesive unit

**Attributes**:
- Name: `todo-chatbot`
- Version: 1.0.0
- App Version: 1.0.0
- Description: Todo Chatbot application deployment for Minikube

**Managed Resources**:
- Frontend Deployment
- Backend Deployment
- Frontend Service
- Backend Service
- ConfigMap
- Secrets

**Configuration**:
- Values file: `values.yaml`
- Templates: `templates/*.yaml`
- Helpers: `templates/_helpers.tpl`

**Relationships**:
- Manages: All Kubernetes resources
- Configured via: values.yaml
- Installed by: Helm CLI
- Versioned independently: Chart version tracks deployment version

---

## Resource Relationships Diagram

```
Helm Chart (todo-chatbot)
│
├── Frontend Deployment
│   ├── Manages: Frontend Pods (replicas)
│   ├── Uses Image: todo-frontend:v1.0.0
│   ├── Consumes: ConfigMap (environment variables)
│   └── Exposes: Port 3000
│
├── Frontend Service (NodePort)
│   ├── Selects: Frontend Pods
│   ├── Exposes: Port 3000 externally
│   └── Accessed by: External users via Minikube
│
├── Backend Deployment
│   ├── Manages: Backend Pods (replicas)
│   ├── Uses Image: todo-backend:v1.0.0
│   ├── Consumes: Secrets (DATABASE_URL, JWT_SECRET)
│   ├── Consumes: ConfigMap (environment variables)
│   ├── Depends on: External Database (Neon PostgreSQL)
│   └── Exposes: Port 8000
│
├── Backend Service (ClusterIP)
│   ├── Selects: Backend Pods
│   ├── Exposes: Port 8000 internally
│   ├── DNS: todo-backend-service.default.svc.cluster.local
│   └── Accessed by: Frontend Pods
│
├── ConfigMap (todo-chatbot-config)
│   ├── Stores: Non-sensitive configuration
│   └── Consumed by: Frontend and Backend Deployments
│
└── Secrets (todo-chatbot-secrets)
    ├── Stores: DATABASE_URL, JWT_SECRET (base64 encoded)
    └── Consumed by: Backend Deployment
```

## Communication Flow

1. **External User → Frontend**:
   - User accesses Minikube service URL
   - Request routes to Frontend Service (NodePort)
   - Frontend Service routes to Frontend Pod
   - Frontend Pod serves Next.js application

2. **Frontend → Backend**:
   - Frontend makes API call to backend
   - Uses service discovery: `http://todo-backend-service:8000/api`
   - Kubernetes DNS resolves service name to ClusterIP
   - Backend Service routes to Backend Pod
   - Backend Pod processes request and returns response

3. **Backend → Database**:
   - Backend connects to external Neon PostgreSQL
   - Uses DATABASE_URL from Secrets
   - Connection established outside Kubernetes cluster
   - Database operations performed via SQLModel ORM

## State Management

**Stateless Services**:
- Frontend Deployment: No persistent state
- Backend Deployment: No persistent state (database is external)

**Configuration State**:
- ConfigMap: Mutable (can be updated)
- Secrets: Mutable (can be updated)
- Helm values: Versioned in values.yaml

**Deployment State**:
- Managed by Kubernetes Deployment controller
- Rolling updates supported
- Rollback supported via Helm or kubectl

## Scaling Considerations

**Horizontal Scaling** (not implemented in Phase IV but supported):
- Frontend: Can scale to multiple replicas
- Backend: Can scale to multiple replicas
- Service: Automatically load balances across replicas

**Vertical Scaling**:
- Resource limits can be adjusted via Helm values
- Requires pod restart to apply new limits

**Limitations**:
- Single replica for Phase IV (local development)
- No autoscaling configured
- No persistent volumes (stateless design)

## Resource Dependencies

**Deployment Order** (managed by Kubernetes):
1. Namespace (if custom namespace used)
2. ConfigMap and Secrets (must exist before Deployments)
3. Deployments (can be created in any order)
4. Services (can be created before or after Deployments)

**Runtime Dependencies**:
- Backend requires: Secrets (DATABASE_URL, JWT_SECRET)
- Backend requires: External database connectivity
- Frontend requires: Backend Service (for API calls)
- Frontend requires: ConfigMap (for API_BASE_URL)

## Validation Criteria

**Resource Creation**:
- All resources created successfully by Helm
- No errors in Helm install output
- Resources visible via `kubectl get all`

**Pod Health**:
- All pods reach Running state
- Liveness probes passing
- Readiness probes passing
- No crash loops or restarts

**Service Connectivity**:
- Services have endpoints
- Frontend Service accessible via Minikube
- Backend Service resolvable via DNS
- Frontend can reach Backend API

**Configuration**:
- ConfigMap data correct
- Secrets mounted correctly
- Environment variables injected
- Application functionality preserved

# Research: Production Cloud Deployment

**Feature**: 006-cloud-deployment
**Date**: 2026-02-09
**Purpose**: Document research findings and technical decisions for deploying Todo application to cloud Kubernetes

---

## Research Area 1: Cloud Kubernetes Cluster Setup

### Oracle Cloud Kubernetes Engine (OKE)

**Cluster Creation**:
- OCI Console → Developer Services → Kubernetes Clusters (OKE)
- Quick Create workflow provisions VCN, subnets, node pools automatically
- Minimum 2 worker nodes recommended for high availability
- Node shape: VM.Standard.E4.Flex (1 OCPU, 16GB RAM per node)

**kubectl Configuration**:
```bash
oci ce cluster create-kubeconfig --cluster-id <cluster-ocid> --file ~/.kube/config --region <region>
export KUBECONFIG=~/.kube/config
kubectl get nodes
```

**Storage Classes**:
- Default: `oci-bv` (OCI Block Volume)
- Supports dynamic provisioning via CSI driver
- Persistent volumes automatically created in OCI Block Storage

### Azure Kubernetes Service (AKS)

**Cluster Creation**:
```bash
az aks create --resource-group <rg-name> --name <cluster-name> \
  --node-count 2 --node-vm-size Standard_DS2_v2 \
  --enable-managed-identity --generate-ssh-keys
```

**kubectl Configuration**:
```bash
az aks get-credentials --resource-group <rg-name> --name <cluster-name>
kubectl get nodes
```

**Storage Classes**:
- Default: `default` (Azure Disk)
- `azurefile` for ReadWriteMany volumes
- Supports dynamic provisioning via Azure CSI drivers

### Google Kubernetes Engine (GKE)

**Cluster Creation**:
```bash
gcloud container clusters create <cluster-name> \
  --num-nodes=2 --machine-type=e2-standard-2 \
  --zone=us-central1-a
```

**kubectl Configuration**:
```bash
gcloud container clusters get-credentials <cluster-name> --zone=us-central1-a
kubectl get nodes
```

**Storage Classes**:
- Default: `standard` (GCE Persistent Disk)
- `standard-rwo` for ReadWriteOnce volumes
- Supports dynamic provisioning via GCE CSI driver

### Common Requirements

**Minimum Cluster Specifications**:
- 2 worker nodes (for high availability)
- 2 vCPUs per node (4 vCPUs total)
- 4 GB RAM per node (8 GB total)
- 50 GB disk per node
- Kubernetes version 1.28+

**Network Requirements**:
- Outbound internet access for pulling Docker images
- LoadBalancer service type support (cloud provider integration)
- Network policies support (optional but recommended)

**RBAC Configuration**:
- Cluster admin access for initial setup
- Service accounts for Dapr and application services
- Role bindings for namespace-scoped permissions

---

## Research Area 2: Helm Chart Best Practices

### Helm 3.x Chart Structure

**Standard Directory Layout**:
```
chart-name/
├── Chart.yaml          # Chart metadata (name, version, dependencies)
├── values.yaml         # Default configuration values
├── templates/          # Kubernetes manifest templates
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── _helpers.tpl   # Template helpers and partials
│   └── NOTES.txt      # Post-install instructions
└── charts/            # Subchart dependencies (optional)
```

**Chart.yaml Best Practices**:
- Use semantic versioning (e.g., 1.0.0)
- Specify `apiVersion: v2` for Helm 3
- Define dependencies with version constraints
- Include description, maintainers, and keywords

**values.yaml Organization**:
- Group related values hierarchically
- Provide sensible defaults for all values
- Document each value with inline comments
- Use consistent naming conventions (camelCase)

### Umbrella Charts vs Independent Charts

**Umbrella Chart Approach** (Chosen):
- Single parent chart with multiple subcharts as dependencies
- Shared configuration via global values
- Single `helm install` command deploys entire stack
- Subcharts can still be deployed independently

**Implementation**:
```yaml
# Chart.yaml for umbrella chart
dependencies:
  - name: frontend
    version: 1.0.0
    repository: "file://charts/frontend"
  - name: backend
    version: 1.0.0
    repository: "file://charts/backend"
```

### Values File Organization

**Environment-Specific Values**:
- `values.yaml`: Default values (Minikube/dev)
- `values-dev.yaml`: Development environment overrides
- `values-staging.yaml`: Staging environment overrides
- `values-prod.yaml`: Production environment overrides

**Usage**:
```bash
# Development
helm install todo-app ./helm/todo-app -f values-dev.yaml

# Production
helm install todo-app ./helm/todo-app -f values-prod.yaml
```

### Chart Dependencies and Version Management

**Dependency Management**:
```bash
# Update dependencies
helm dependency update ./helm/todo-app

# List dependencies
helm dependency list ./helm/todo-app
```

**Version Constraints**:
- Use exact versions for production stability
- Use version ranges for development flexibility
- Lock dependencies with `Chart.lock` file

### Helm Hooks

**Pre/Post-Deployment Tasks**:
- `pre-install`: Run before chart installation (e.g., database migrations)
- `post-install`: Run after chart installation (e.g., smoke tests)
- `pre-upgrade`: Run before chart upgrade
- `post-upgrade`: Run after chart upgrade

**Example**:
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  annotations:
    "helm.sh/hook": pre-install
    "helm.sh/hook-weight": "0"
```

### Chart Testing and Validation

**Validation Commands**:
```bash
# Lint chart for errors
helm lint ./helm/todo-app

# Render templates without installing
helm template todo-app ./helm/todo-app

# Dry-run installation
helm install todo-app ./helm/todo-app --dry-run --debug
```

---

## Research Area 3: Dapr Installation on Kubernetes

### Dapr CLI Installation

**Installation Methods**:
```bash
# Linux/macOS
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Windows (PowerShell)
powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"

# Verify installation
dapr version
```

### Dapr Control Plane Installation

**Initialize Dapr in Kubernetes**:
```bash
# Install Dapr control plane
dapr init -k

# Verify installation
dapr status -k

# Expected output:
# NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS  VERSION  AGE  CREATED
# dapr-operator          dapr-system  True     Running  1         1.12.0   30s  2024-02-09 10:00:00
# dapr-sidecar-injector  dapr-system  True     Running  1         1.12.0   30s  2024-02-09 10:00:00
# dapr-sentry            dapr-system  True     Running  1         1.12.0   30s  2024-02-09 10:00:00
# dapr-placement-server  dapr-system  True     Running  1         1.12.0   30s  2024-02-09 10:00:00
```

### Dapr Control Plane Components

**dapr-operator**:
- Manages Dapr component CRDs
- Watches for component updates and applies them
- Handles component lifecycle

**dapr-sidecar-injector**:
- Mutating webhook that injects Dapr sidecar into pods
- Triggered by `dapr.io/enabled: "true"` annotation
- Configures sidecar based on annotations

**dapr-sentry**:
- Certificate authority for mTLS between services
- Issues and rotates certificates automatically
- Enables secure service-to-service communication

**dapr-placement-server**:
- Manages actor placement and distribution
- Not required for Pub/Sub (but installed by default)

### Dapr Component CRD Configuration

**Pub/Sub Component Example**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub-kafka
  namespace: todo-app
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "kafka:9092"
  - name: consumerGroup
    value: "dapr-consumer-group"
  - name: authType
    value: "none"
```

### Dapr Sidecar Injection

**Deployment Annotations**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  template:
    metadata:
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "backend"
        dapr.io/app-port: "8000"
        dapr.io/log-level: "info"
```

**Sidecar Configuration**:
- `dapr.io/enabled`: Enable Dapr sidecar injection
- `dapr.io/app-id`: Unique identifier for the service
- `dapr.io/app-port`: Port the application listens on
- `dapr.io/log-level`: Logging verbosity (debug, info, warn, error)

### Dapr Telemetry Configuration

**Distributed Tracing**:
- Dapr automatically exports traces to configured backend
- Supports Zipkin, Jaeger, OpenTelemetry
- Traces include service-to-service calls and Pub/Sub operations

**Metrics**:
- Dapr exposes Prometheus metrics on port 9090
- Metrics include request latency, error rates, throughput
- Can be scraped by Prometheus for monitoring

---

## Research Area 4: Kafka Deployment Strategies

### Kafka StatefulSet Configuration

**Why StatefulSet**:
- Stable network identities (kafka-0, kafka-1, kafka-2)
- Persistent storage per pod
- Ordered deployment and scaling
- Required for Kafka cluster formation

**Resource Requirements**:
- **CPU**: 500m request, 2000m limit per broker
- **Memory**: 1Gi request, 4Gi limit per broker
- **Storage**: 10Gi PersistentVolume per broker (minimum)

**Example StatefulSet**:
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: kafka
spec:
  serviceName: kafka
  replicas: 1  # Single broker for Phase V - Part C
  selector:
    matchLabels:
      app: kafka
  template:
    metadata:
      labels:
        app: kafka
    spec:
      containers:
      - name: kafka
        image: confluentinc/cp-kafka:7.5.0
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 2000m
            memory: 4Gi
  volumeClaimTemplates:
  - metadata:
      name: kafka-data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
```

### Zookeeper vs KRaft Mode

**Zookeeper Mode** (Chosen for Phase V - Part C):
- Traditional Kafka coordination mechanism
- Requires separate Zookeeper deployment
- Well-tested and stable
- Easier to troubleshoot

**KRaft Mode**:
- New Kafka coordination without Zookeeper
- Simpler architecture (fewer components)
- Still in early adoption phase
- Not chosen due to maturity concerns

### PersistentVolume Configuration

**Storage Requirements**:
- Kafka: 10Gi per broker (logs and data)
- Zookeeper: 5Gi (metadata and snapshots)
- Access mode: ReadWriteOnce (single node attachment)
- Reclaim policy: Retain (prevent data loss on deletion)

**Dynamic Provisioning**:
- Cloud providers automatically provision volumes
- Storage class determines volume type (SSD, HDD)
- Volumes persist across pod restarts

### Kafka Topic Creation

**Automatic Topic Creation**:
- Kafka can auto-create topics on first message
- Not recommended for production (no control over partitions/replication)

**Manual Topic Creation** (Recommended):
```bash
# Create task-events topic
kubectl exec -it kafka-0 -- kafka-topics --create \
  --topic task-events \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 1

# Create reminders topic
kubectl exec -it kafka-0 -- kafka-topics --create \
  --topic reminders \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 1
```

### Kafka Monitoring

**Health Checks**:
- Liveness probe: Check Kafka process is running
- Readiness probe: Check Kafka can accept connections

**Metrics**:
- JMX metrics exposed by Kafka
- Can be scraped by Prometheus JMX exporter
- Key metrics: throughput, latency, consumer lag

---

## Research Area 5: Secrets Management

### Kubernetes Secrets Creation

**Manual Creation**:
```bash
# Create secret from literal values
kubectl create secret generic app-secrets \
  --from-literal=DATABASE_URL="postgresql://..." \
  --from-literal=JWT_SECRET="your-secret-key" \
  --namespace=todo-app

# Create secret from file
kubectl create secret generic app-secrets \
  --from-file=database-url=./secrets/database-url.txt \
  --from-file=jwt-secret=./secrets/jwt-secret.txt \
  --namespace=todo-app
```

**Declarative Creation** (Helm Template):
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: {{ .Values.namespace }}
type: Opaque
data:
  DATABASE_URL: {{ .Values.secrets.databaseUrl | b64enc }}
  JWT_SECRET: {{ .Values.secrets.jwtSecret | b64enc }}
```

### Environment Variable Injection

**From Secret**:
```yaml
env:
- name: DATABASE_URL
  valueFrom:
    secretKeyRef:
      name: app-secrets
      key: DATABASE_URL
- name: JWT_SECRET
  valueFrom:
    secretKeyRef:
      name: app-secrets
      key: JWT_SECRET
```

### Secret Rotation

**Manual Rotation**:
1. Update secret value: `kubectl edit secret app-secrets`
2. Restart pods to pick up new value: `kubectl rollout restart deployment/backend`

**Automated Rotation**:
- External Secrets Operator (out of scope for Phase V - Part C)
- Reloader operator (watches secrets and restarts pods automatically)

### Secret Encryption at Rest

**Cloud Provider Encryption**:
- Secrets encrypted at rest by default in managed Kubernetes
- Uses cloud provider's KMS (Key Management Service)
- No additional configuration required

---

## Research Area 6: Ingress and Load Balancing

### LoadBalancer Service Type

**Cloud Provider Integration**:
- Automatically provisions cloud load balancer
- Assigns external IP address
- Routes traffic to service pods

**Example**:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 3000
  selector:
    app: frontend
```

**Getting External IP**:
```bash
kubectl get svc frontend -n todo-app
# NAME       TYPE           CLUSTER-IP     EXTERNAL-IP      PORT(S)        AGE
# frontend   LoadBalancer   10.96.0.1      203.0.113.1      80:30080/TCP   5m
```

### Ingress Controller Options

**Nginx Ingress Controller** (Most Popular):
- Open-source, widely adopted
- Supports path-based routing, TLS termination
- Easy to configure

**Traefik**:
- Modern, cloud-native ingress controller
- Automatic service discovery
- Built-in dashboard

**Cloud-Native Controllers**:
- GKE: GCE Ingress Controller
- AKS: Application Gateway Ingress Controller
- OKE: OCI Load Balancer

**Decision**: Use LoadBalancer for Phase V - Part C (simpler), Ingress optional for advanced routing

---

## Research Area 7: Resource Management

### Resource Requests and Limits

**Best Practices**:
- **Requests**: Guaranteed resources, used for scheduling
- **Limits**: Maximum resources, enforced by kubelet
- Set requests = limits for guaranteed QoS class
- Set requests < limits for burstable QoS class

**Example**:
```yaml
resources:
  requests:
    cpu: 200m      # 0.2 CPU cores
    memory: 256Mi  # 256 MiB
  limits:
    cpu: 1000m     # 1 CPU core
    memory: 1Gi    # 1 GiB
```

### Horizontal Pod Autoscaler (HPA)

**Configuration**:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

**Decision**: HPA out of scope for Phase V - Part C (manual scaling sufficient)

### Resource Quotas

**Namespace-Level Quotas**:
```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: todo-app-quota
  namespace: todo-app
spec:
  hard:
    requests.cpu: "4"
    requests.memory: 8Gi
    limits.cpu: "8"
    limits.memory: 16Gi
    pods: "20"
```

---

## Research Area 8: Deployment Validation

### Health Check Endpoints

**Liveness Probe**:
- Checks if application is alive
- Restarts pod if probe fails
- Example: `/health` endpoint returns 200 OK

**Readiness Probe**:
- Checks if application is ready to serve traffic
- Removes pod from service endpoints if probe fails
- Example: `/ready` endpoint checks database connection

**Configuration**:
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /ready
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3
```

### Deployment Rollout Strategies

**RollingUpdate** (Default):
- Gradually replaces old pods with new pods
- Zero downtime deployment
- Configurable max surge and max unavailable

**Recreate**:
- Terminates all old pods before creating new pods
- Downtime during deployment
- Simpler, faster for non-critical services

**Configuration**:
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1        # Max 1 extra pod during update
    maxUnavailable: 0  # Always maintain min replicas
```

### Rollback Procedures

**Helm Rollback**:
```bash
# List release history
helm history todo-app

# Rollback to previous version
helm rollback todo-app

# Rollback to specific revision
helm rollback todo-app 3
```

**kubectl Rollback**:
```bash
# Rollback deployment
kubectl rollout undo deployment/backend -n todo-app

# Rollback to specific revision
kubectl rollout undo deployment/backend --to-revision=2 -n todo-app
```

### Post-Deployment Validation

**Smoke Tests**:
1. Check all pods running: `kubectl get pods -n todo-app`
2. Check services have endpoints: `kubectl get endpoints -n todo-app`
3. Test frontend accessibility: `curl http://<external-ip>`
4. Test backend health: `kubectl exec -it <backend-pod> -- curl localhost:8000/health`
5. Test event flow: Create task, verify recurring task created

---

## Summary of Key Decisions

1. **Helm Chart Organization**: Umbrella chart with subcharts
2. **Dapr Installation**: Dapr CLI (`dapr init -k`)
3. **Kafka Deployment**: Custom StatefulSet with Zookeeper
4. **Secrets Management**: Kubernetes Secrets with manual creation
5. **Frontend Access**: LoadBalancer service type
6. **Environment Configuration**: Separate Helm values files per environment
7. **Deployment Order**: Sequential with validation checkpoints
8. **Rollback Strategy**: Helm rollback command

All decisions prioritize simplicity, cloud-agnosticism, and alignment with Phase V - Part C constitution principles.

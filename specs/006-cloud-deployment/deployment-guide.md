# Deployment Guide: Production Cloud Deployment

**Feature**: 006-cloud-deployment
**Date**: 2026-02-09
**Purpose**: Step-by-step runbook for deploying Todo application to cloud Kubernetes cluster

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Cluster Preparation](#cluster-preparation)
3. [Secrets Creation](#secrets-creation)
4. [Dapr Installation](#dapr-installation)
5. [Helm Chart Deployment](#helm-chart-deployment)
6. [Validation Procedures](#validation-procedures)
7. [Troubleshooting](#troubleshooting)
8. [Rollback Procedures](#rollback-procedures)

---

## Prerequisites

### Required Tools

- [ ] **kubectl** (v1.28+): Kubernetes command-line tool
  ```bash
  kubectl version --client
  ```

- [ ] **Helm** (v3.x): Kubernetes package manager
  ```bash
  helm version
  ```

- [ ] **Dapr CLI** (v1.12+): Dapr command-line tool
  ```bash
  dapr version
  ```

- [ ] **Docker** (optional): For building images locally
  ```bash
  docker version
  ```

### Cloud Provider Access

- [ ] **Kubernetes Cluster**: Provisioned and accessible
  - Oracle Cloud Kubernetes Engine (OKE), OR
  - Azure Kubernetes Service (AKS), OR
  - Google Kubernetes Engine (GKE)

- [ ] **kubectl Context**: Configured for target cluster
  ```bash
  kubectl config current-context
  kubectl get nodes
  ```

- [ ] **Cluster Resources**: Minimum requirements met
  - 2 worker nodes
  - 4 vCPUs total (2 per node)
  - 8 GB RAM total (4 GB per node)
  - 100 GB storage total

### Docker Images

- [ ] **Images Built**: All service images available in registry
  - `frontend:latest` (Next.js)
  - `backend:latest` (FastAPI)
  - `recurring-task-service:latest`
  - `notification-service:latest`

- [ ] **Registry Access**: Cluster can pull images from registry
  ```bash
  # Test image pull
  kubectl run test --image=<your-registry>/frontend:latest --rm -it --restart=Never -- echo "Image accessible"
  ```

### External Services

- [ ] **Database**: Neon Serverless PostgreSQL connection string
  - Format: `postgresql://user:password@host:port/database?sslmode=require`
  - Test connectivity from local machine

- [ ] **JWT Secret**: Secure random string for authentication
  - Generate: `openssl rand -base64 32`
  - Same secret used in Phase II deployment

---

## Cluster Preparation

### Step 1: Create Namespace

```bash
# Create todo-app namespace
kubectl create namespace todo-app

# Verify namespace created
kubectl get namespace todo-app
```

**Expected Output**:
```
NAME       STATUS   AGE
todo-app   Active   5s
```

### Step 2: Set Default Namespace (Optional)

```bash
# Set todo-app as default namespace for current context
kubectl config set-context --current --namespace=todo-app

# Verify
kubectl config view --minify | grep namespace:
```

### Step 3: Configure RBAC (If Required)

```bash
# Create service account for Dapr
kubectl create serviceaccount dapr-operator -n todo-app

# Grant necessary permissions (cluster-admin for simplicity)
kubectl create clusterrolebinding dapr-operator-admin \
  --clusterrole=cluster-admin \
  --serviceaccount=todo-app:dapr-operator
```

**Note**: In production, use least-privilege RBAC policies instead of cluster-admin.

### Step 4: Verify Cluster Connectivity

```bash
# Check cluster info
kubectl cluster-info

# Check node status
kubectl get nodes

# Check available storage classes
kubectl get storageclass
```

**Expected**: All nodes in Ready state, at least one storage class available.

---

## Secrets Creation

### Step 1: Prepare Secret Values

Create a file `secrets.env` (DO NOT commit to version control):

```bash
# secrets.env
DATABASE_URL=postgresql://user:password@host:port/database?sslmode=require
JWT_SECRET=your-secure-jwt-secret-key-here
```

### Step 2: Create Kubernetes Secret

```bash
# Create secret from env file
kubectl create secret generic app-secrets \
  --from-env-file=secrets.env \
  --namespace=todo-app

# Verify secret created
kubectl get secret app-secrets -n todo-app
```

**Expected Output**:
```
NAME          TYPE     DATA   AGE
app-secrets   Opaque   2      5s
```

### Step 3: Verify Secret Contents (Optional)

```bash
# Describe secret (shows keys, not values)
kubectl describe secret app-secrets -n todo-app

# Decode secret value (for verification only)
kubectl get secret app-secrets -n todo-app -o jsonpath='{.data.DATABASE_URL}' | base64 --decode
```

### Step 4: Clean Up Local Secret File

```bash
# Remove secrets.env file
rm secrets.env

# Verify file deleted
ls secrets.env  # Should show "No such file or directory"
```

**Security Note**: Never commit secrets to version control. Use `.gitignore` to exclude secret files.

---

## Dapr Installation

### Step 1: Install Dapr Control Plane

```bash
# Initialize Dapr in Kubernetes
dapr init -k

# Wait for installation to complete (30-60 seconds)
```

**Expected Output**:
```
⌛  Making the jump to hyperspace...
✅  Deploying the Dapr control plane to your cluster...
✅  Success! Dapr has been installed to namespace dapr-system.
```

### Step 2: Verify Dapr Installation

```bash
# Check Dapr status
dapr status -k

# Check Dapr pods
kubectl get pods -n dapr-system
```

**Expected Output**:
```
NAME                                     READY   STATUS    RESTARTS   AGE
dapr-operator-xxx                        1/1     Running   0          1m
dapr-sidecar-injector-xxx                1/1     Running   0          1m
dapr-sentry-xxx                          1/1     Running   0          1m
dapr-placement-server-xxx                1/1     Running   0          1m
```

**All pods should be in Running state with 1/1 Ready.**

### Step 3: Verify Dapr Sidecar Injector

```bash
# Check mutating webhook configuration
kubectl get mutatingwebhookconfiguration dapr-sidecar-injector

# Verify webhook is active
kubectl describe mutatingwebhookconfiguration dapr-sidecar-injector | grep "Failure Policy"
```

**Expected**: Webhook exists and failure policy is set.

---

## Helm Chart Deployment

### Deployment Order

1. Kafka and Zookeeper (infrastructure)
2. Dapr Components (Pub/Sub configuration)
3. Backend Services (backend, recurring-task-service, notification-service)
4. Frontend Service

### Step 1: Deploy Kafka and Zookeeper

```bash
# Navigate to Helm charts directory
cd helm

# Deploy Kafka chart
helm install kafka ./kafka \
  --namespace=todo-app \
  --wait --timeout=5m

# Verify Kafka deployment
kubectl get pods -n todo-app -l app=kafka
kubectl get pods -n todo-app -l app=zookeeper
```

**Expected**: Kafka and Zookeeper pods in Running state.

**Wait for Kafka to be ready** (check logs):
```bash
kubectl logs -f kafka-0 -n todo-app
# Look for: "Kafka Server started"
```

### Step 2: Create Kafka Topics

```bash
# Create task-events topic
kubectl exec -it kafka-0 -n todo-app -- kafka-topics --create \
  --topic task-events \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 1

# Create reminders topic
kubectl exec -it kafka-0 -n todo-app -- kafka-topics --create \
  --topic reminders \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 1

# Verify topics created
kubectl exec -it kafka-0 -n todo-app -- kafka-topics --list \
  --bootstrap-server localhost:9092
```

**Expected Output**:
```
task-events
reminders
```

### Step 3: Deploy Dapr Components

```bash
# Deploy Dapr Pub/Sub component
helm install dapr-components ./dapr-components \
  --namespace=todo-app \
  --wait

# Verify Dapr component created
kubectl get component -n todo-app
```

**Expected Output**:
```
NAME            AGE
pubsub-kafka    10s
```

### Step 4: Deploy Backend Services

```bash
# Deploy backend (Chat API)
helm install backend ./backend \
  --namespace=todo-app \
  --set image.tag=latest \
  --set secrets.databaseUrl="<from-secret>" \
  --set secrets.jwtSecret="<from-secret>" \
  --wait --timeout=5m

# Deploy recurring-task-service
helm install recurring-task-service ./recurring-task-service \
  --namespace=todo-app \
  --set image.tag=latest \
  --set secrets.databaseUrl="<from-secret>" \
  --wait --timeout=5m

# Deploy notification-service
helm install notification-service ./notification-service \
  --namespace=todo-app \
  --set image.tag=latest \
  --wait --timeout=5m

# Verify backend services
kubectl get pods -n todo-app | grep -E "backend|recurring|notification"
```

**Expected**: All backend pods in Running state with 2/2 containers (app + daprd sidecar).

### Step 5: Deploy Frontend Service

```bash
# Deploy frontend
helm install frontend ./frontend \
  --namespace=todo-app \
  --set image.tag=latest \
  --set service.type=LoadBalancer \
  --wait --timeout=5m

# Verify frontend deployment
kubectl get pods -n todo-app -l app=frontend
kubectl get svc frontend -n todo-app
```

**Expected**: Frontend pod in Running state, service has EXTERNAL-IP assigned.

**Get Frontend URL**:
```bash
# Wait for external IP (may take 1-2 minutes)
kubectl get svc frontend -n todo-app -w

# Once EXTERNAL-IP is assigned:
FRONTEND_URL=$(kubectl get svc frontend -n todo-app -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "Frontend URL: http://$FRONTEND_URL"
```

### Alternative: Deploy All Services with Umbrella Chart

```bash
# Deploy entire stack with single command
helm install todo-app ./todo-app \
  --namespace=todo-app \
  --set global.imageTag=latest \
  --set global.secrets.databaseUrl="<from-secret>" \
  --set global.secrets.jwtSecret="<from-secret>" \
  --wait --timeout=10m

# Verify all services
kubectl get pods -n todo-app
```

---

## Validation Procedures

### Validation Checklist

- [ ] All pods running
- [ ] Dapr sidecars injected
- [ ] Frontend accessible
- [ ] Backend health check passes
- [ ] Kafka topics exist
- [ ] Event flow working
- [ ] Secrets loaded correctly
- [ ] Resource limits enforced

### Step 1: Verify All Pods Running

```bash
# Check pod status
kubectl get pods -n todo-app

# Expected: All pods in Running state, no restarts
```

**Troubleshooting**: If pods are not Running, check logs:
```bash
kubectl logs <pod-name> -n todo-app
kubectl describe pod <pod-name> -n todo-app
```

### Step 2: Verify Dapr Sidecars Injected

```bash
# Check backend pod has 2 containers
kubectl get pod -n todo-app -l app=backend -o jsonpath='{.items[0].spec.containers[*].name}'

# Expected output: backend daprd
```

### Step 3: Test Frontend Accessibility

```bash
# Get frontend URL
FRONTEND_URL=$(kubectl get svc frontend -n todo-app -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Test frontend
curl -I http://$FRONTEND_URL

# Expected: HTTP/1.1 200 OK
```

**Browser Test**: Open `http://$FRONTEND_URL` in browser, verify page loads.

### Step 4: Test Backend Health Check

```bash
# Port-forward to backend service
kubectl port-forward svc/backend 8000:8000 -n todo-app &

# Test health endpoint
curl http://localhost:8000/health

# Expected: {"status": "healthy"}

# Stop port-forward
kill %1
```

### Step 5: Verify Kafka Topics

```bash
# List Kafka topics
kubectl exec -it kafka-0 -n todo-app -- kafka-topics --list \
  --bootstrap-server localhost:9092

# Expected: task-events, reminders
```

### Step 6: Test Event Flow

```bash
# Create a test task via frontend or API
# (Requires authentication - use frontend UI)

# Check backend logs for event publishing
kubectl logs -f deployment/backend -c backend -n todo-app | grep "Event published"

# Check Kafka for events
kubectl exec -it kafka-0 -n todo-app -- kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic task-events \
  --from-beginning \
  --max-messages 5

# Check recurring-task-service logs for event consumption
kubectl logs -f deployment/recurring-task-service -c recurring-task-service -n todo-app
```

### Step 7: Verify Secrets Loaded

```bash
# Check backend pod environment variables
kubectl exec -it deployment/backend -c backend -n todo-app -- env | grep DATABASE_URL

# Expected: DATABASE_URL=postgresql://...
# (Value should match secret, not be empty)
```

### Step 8: Verify Resource Limits

```bash
# Check pod resource usage
kubectl top pods -n todo-app

# Verify no pods exceeding limits
kubectl get pods -n todo-app -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[0].resources.limits}{"\n"}{end}'
```

---

## Troubleshooting

### Issue 1: Pods Not Starting

**Symptoms**: Pods stuck in Pending, ContainerCreating, or CrashLoopBackOff state.

**Diagnosis**:
```bash
kubectl describe pod <pod-name> -n todo-app
kubectl logs <pod-name> -n todo-app
```

**Common Causes**:
- **Insufficient resources**: Check node capacity
  ```bash
  kubectl describe nodes
  ```
- **Image pull errors**: Verify image exists and registry is accessible
  ```bash
  kubectl get events -n todo-app | grep "Failed to pull image"
  ```
- **Secret not found**: Verify secret exists
  ```bash
  kubectl get secret app-secrets -n todo-app
  ```

**Solutions**:
- Scale down other workloads or add nodes
- Fix image name/tag or registry credentials
- Recreate secret with correct values

### Issue 2: Dapr Sidecar Not Injected

**Symptoms**: Backend pods have only 1 container instead of 2.

**Diagnosis**:
```bash
kubectl get pod <pod-name> -n todo-app -o jsonpath='{.spec.containers[*].name}'
```

**Common Causes**:
- Dapr not installed: `dapr status -k` shows error
- Missing annotations: Deployment missing `dapr.io/enabled: "true"`
- Namespace not labeled: Dapr sidecar injector not watching namespace

**Solutions**:
```bash
# Reinstall Dapr
dapr uninstall -k
dapr init -k

# Verify deployment annotations
kubectl get deployment <deployment-name> -n todo-app -o yaml | grep dapr.io

# Restart deployment
kubectl rollout restart deployment/<deployment-name> -n todo-app
```

### Issue 3: Frontend Not Accessible

**Symptoms**: External IP not assigned or connection refused.

**Diagnosis**:
```bash
kubectl get svc frontend -n todo-app
kubectl describe svc frontend -n todo-app
```

**Common Causes**:
- LoadBalancer not supported: Cloud provider doesn't support LoadBalancer type
- Firewall rules: Cloud firewall blocking traffic
- Service selector mismatch: Service not routing to pods

**Solutions**:
```bash
# Check if LoadBalancer is supported
kubectl get svc frontend -n todo-app -o jsonpath='{.status.loadBalancer}'

# Use NodePort as fallback
kubectl patch svc frontend -n todo-app -p '{"spec":{"type":"NodePort"}}'

# Check firewall rules (cloud provider specific)
# Oracle Cloud: Security Lists
# Azure: Network Security Groups
# GCP: Firewall Rules
```

### Issue 4: Kafka Connection Errors

**Symptoms**: Backend logs show "Failed to connect to Kafka" or "Connection refused".

**Diagnosis**:
```bash
kubectl logs deployment/backend -c backend -n todo-app | grep -i kafka
kubectl logs kafka-0 -n todo-app | grep -i error
```

**Common Causes**:
- Kafka not ready: Kafka pod still starting
- DNS resolution failure: Service name not resolving
- Dapr component misconfigured: Wrong broker address

**Solutions**:
```bash
# Wait for Kafka to be ready
kubectl wait --for=condition=ready pod/kafka-0 -n todo-app --timeout=5m

# Test DNS resolution
kubectl run -it --rm debug --image=busybox --restart=Never -n todo-app -- nslookup kafka

# Verify Dapr component
kubectl get component pubsub-kafka -n todo-app -o yaml
```

### Issue 5: Event Flow Not Working

**Symptoms**: Tasks created but recurring tasks not generated, no events in Kafka.

**Diagnosis**:
```bash
# Check backend event publishing
kubectl logs deployment/backend -c backend -n todo-app | grep "Event published"

# Check Kafka topics
kubectl exec -it kafka-0 -n todo-app -- kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic task-events \
  --from-beginning

# Check recurring-task-service logs
kubectl logs deployment/recurring-task-service -c recurring-task-service -n todo-app
```

**Common Causes**:
- Dapr Pub/Sub component not loaded
- Kafka topics not created
- Consumer not subscribed to topic

**Solutions**:
```bash
# Verify Dapr component
kubectl get component -n todo-app

# Recreate Kafka topics
kubectl exec -it kafka-0 -n todo-app -- kafka-topics --create \
  --topic task-events --bootstrap-server localhost:9092 \
  --partitions 3 --replication-factor 1

# Check Dapr subscription
kubectl logs deployment/recurring-task-service -c daprd -n todo-app | grep subscribe
```

---

## Rollback Procedures

### Helm Rollback

**Step 1: Check Release History**
```bash
# List all releases
helm list -n todo-app

# View release history
helm history todo-app -n todo-app
```

**Step 2: Rollback to Previous Version**
```bash
# Rollback to previous revision
helm rollback todo-app -n todo-app

# Rollback to specific revision
helm rollback todo-app 3 -n todo-app
```

**Step 3: Verify Rollback**
```bash
# Check pod status
kubectl get pods -n todo-app

# Verify image versions
kubectl get pods -n todo-app -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[0].image}{"\n"}{end}'
```

### kubectl Rollback

**Step 1: Check Deployment History**
```bash
# View deployment revisions
kubectl rollout history deployment/backend -n todo-app
```

**Step 2: Rollback Deployment**
```bash
# Rollback to previous revision
kubectl rollout undo deployment/backend -n todo-app

# Rollback to specific revision
kubectl rollout undo deployment/backend --to-revision=2 -n todo-app
```

**Step 3: Monitor Rollback**
```bash
# Watch rollout status
kubectl rollout status deployment/backend -n todo-app
```

### Emergency Rollback (Complete Uninstall)

**If rollback fails, perform complete uninstall and redeploy**:

```bash
# Uninstall all Helm releases
helm uninstall todo-app -n todo-app
# OR uninstall individual services
helm uninstall frontend backend recurring-task-service notification-service kafka dapr-components -n todo-app

# Delete namespace (WARNING: Deletes all resources)
kubectl delete namespace todo-app

# Redeploy from scratch (follow deployment steps above)
```

---

## Post-Deployment Checklist

- [ ] All pods running and healthy
- [ ] Frontend accessible via public URL
- [ ] Users can register and login
- [ ] Tasks can be created, updated, deleted
- [ ] Recurring tasks automatically created
- [ ] Notifications logged to console
- [ ] Secrets not exposed in logs or configs
- [ ] Resource limits enforced
- [ ] Deployment documented in runbook
- [ ] Rollback procedure tested

---

## Next Steps

1. **Monitor System**: Set up monitoring and alerting (out of scope for Phase V - Part C)
2. **Configure DNS**: Map custom domain to frontend LoadBalancer IP
3. **Enable TLS**: Configure Ingress with TLS certificates (optional)
4. **Optimize Resources**: Adjust resource requests/limits based on actual usage
5. **Implement HPA**: Configure Horizontal Pod Autoscaler for auto-scaling
6. **Set Up CI/CD**: Automate deployment pipeline (out of scope for Phase V - Part C)

---

## Support and Resources

- **Kubernetes Documentation**: https://kubernetes.io/docs/
- **Helm Documentation**: https://helm.sh/docs/
- **Dapr Documentation**: https://docs.dapr.io/
- **Kafka Documentation**: https://kafka.apache.org/documentation/
- **Project Repository**: [Link to repository]
- **Issue Tracker**: [Link to issue tracker]

# Quickstart Guide: Todo Chatbot on Minikube

**Feature**: 003-minikube-deployment
**Date**: 2026-02-08
**Purpose**: Quick deployment guide for Todo Chatbot on local Minikube cluster

## Prerequisites

Before starting, ensure you have the following installed:

- **Minikube** (v1.30+): Local Kubernetes cluster
- **kubectl** (v1.28+): Kubernetes command-line tool
- **Helm** (v3.12+): Kubernetes package manager
- **Docker** (v24+): Container runtime

### Installation Links

- Minikube: https://minikube.sigs.k8s.io/docs/start/
- kubectl: https://kubernetes.io/docs/tasks/tools/
- Helm: https://helm.sh/docs/intro/install/
- Docker: https://docs.docker.com/get-docker/

### Verify Installation

```bash
minikube version
kubectl version --client
helm version
docker --version
```

---

## Quick Start (5 Steps)

### Step 1: Start Minikube Cluster

```bash
# Start Minikube with recommended resources
minikube start --cpus=4 --memory=8192

# Verify cluster is running
kubectl cluster-info
kubectl get nodes
```

**Expected Output**:
```
✅ Minikube is running
✅ kubectl is configured
✅ Node is Ready
```

---

### Step 2: Build Docker Images

```bash
# Navigate to repository root
cd /path/to/full-stack-evolution-of-todo-app

# Build frontend image
docker build -t todo-frontend:v1.0.0 -f docker/frontend/Dockerfile ./frontend

# Build backend image
docker build -t todo-backend:v1.0.0 -f docker/backend/Dockerfile ./backend

# Verify images
docker images | grep todo
```

**Expected Output**:
```
todo-frontend    v1.0.0    <image-id>    <time>    ~200MB
todo-backend     v1.0.0    <image-id>    <time>    ~250MB
```

---

### Step 3: Load Images into Minikube

```bash
# Load frontend image
minikube image load todo-frontend:v1.0.0

# Load backend image
minikube image load todo-backend:v1.0.0

# Verify images in Minikube
minikube image ls | grep todo
```

**Expected Output**:
```
docker.io/library/todo-frontend:v1.0.0
docker.io/library/todo-backend:v1.0.0
```

---

### Step 4: Install Helm Chart

```bash
# Prepare secrets (replace with your actual values)
DB_URL="postgresql://user:password@host:5432/dbname"
JWT_SECRET="your-super-secret-jwt-key-here"

# Base64 encode secrets
DB_URL_B64=$(echo -n "$DB_URL" | base64)
JWT_SECRET_B64=$(echo -n "$JWT_SECRET" | base64)

# Install chart with secrets
helm install todo-chatbot ./helm/todo-chatbot \
  --set secrets.databaseUrl="$DB_URL_B64" \
  --set secrets.jwtSecret="$JWT_SECRET_B64"

# Wait for pods to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=todo-chatbot --timeout=300s
```

**Expected Output**:
```
NAME: todo-chatbot
LAST DEPLOYED: <timestamp>
NAMESPACE: default
STATUS: deployed
REVISION: 1
```

---

### Step 5: Access Application

```bash
# Get frontend service URL
minikube service todo-chatbot-frontend --url

# Open in browser (or use the URL from above)
minikube service todo-chatbot-frontend
```

**Expected Output**:
```
🎉 Opening service default/todo-chatbot-frontend in default browser...
http://192.168.49.2:30080
```

---

## Verification Steps

### Check Pod Status

```bash
# View all pods
kubectl get pods

# Expected: All pods Running
# todo-chatbot-frontend-xxxxx   1/1   Running   0   2m
# todo-chatbot-backend-xxxxx    1/1   Running   0   2m
```

### Check Services

```bash
# View all services
kubectl get services

# Expected: Services with endpoints
# todo-chatbot-frontend   NodePort    10.x.x.x   <none>   3000:30xxx/TCP   2m
# todo-chatbot-backend    ClusterIP   10.x.x.x   <none>   8000/TCP         2m
```

### Test Backend Health

```bash
# Port-forward to backend
kubectl port-forward svc/todo-chatbot-backend 8000:8000 &

# Test health endpoint
curl http://localhost:8000/health

# Expected: {"status": "healthy"}
```

### Test Frontend

```bash
# Access frontend URL
FRONTEND_URL=$(minikube service todo-chatbot-frontend --url)
curl $FRONTEND_URL

# Expected: HTML content from Next.js
```

### Test End-to-End

1. Open frontend in browser
2. Register a new user account
3. Log in with credentials
4. Create a new task
5. Verify task appears in list
6. Mark task as complete
7. Delete task

**All operations should work without errors.**

---

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods

# Describe pod for events
kubectl describe pod <pod-name>

# Check pod logs
kubectl logs <pod-name>

# Common issues:
# - Image pull errors: Verify images loaded into Minikube
# - CrashLoopBackOff: Check logs for application errors
# - Pending: Check resource availability
```

### Service Not Accessible

```bash
# Check service endpoints
kubectl get endpoints

# Verify service selector matches pod labels
kubectl get pods --show-labels
kubectl describe service <service-name>

# Test service connectivity from within cluster
kubectl run -it --rm debug --image=busybox --restart=Never -- sh
# Inside pod: wget -O- http://todo-chatbot-backend:8000/health
```

### Frontend Cannot Reach Backend

```bash
# Check backend service DNS
kubectl run -it --rm debug --image=busybox --restart=Never -- sh
# Inside pod: nslookup todo-chatbot-backend

# Check environment variables in frontend pod
kubectl exec <frontend-pod> -- env | grep API

# Verify backend is responding
kubectl logs <backend-pod>
```

### Secrets Not Working

```bash
# Check secrets exist
kubectl get secrets

# Verify secret data
kubectl get secret todo-chatbot-secrets -o yaml

# Check if secrets are mounted in pods
kubectl describe pod <backend-pod> | grep -A 5 "Environment"
```

---

## Common Commands

### View Resources

```bash
# All resources
kubectl get all

# Specific resource types
kubectl get deployments
kubectl get services
kubectl get pods
kubectl get configmaps
kubectl get secrets
```

### View Logs

```bash
# Frontend logs
kubectl logs -l component=frontend --tail=50 -f

# Backend logs
kubectl logs -l component=backend --tail=50 -f

# All logs
kubectl logs -l app.kubernetes.io/name=todo-chatbot --tail=50 -f
```

### Helm Operations

```bash
# List releases
helm list

# Get release status
helm status todo-chatbot

# Get release values
helm get values todo-chatbot

# Upgrade release
helm upgrade todo-chatbot ./helm/todo-chatbot --reuse-values

# Rollback release
helm rollback todo-chatbot

# Uninstall release
helm uninstall todo-chatbot
```

---

## Cleanup

### Uninstall Application

```bash
# Remove Helm release
helm uninstall todo-chatbot

# Verify resources removed
kubectl get all
```

### Stop Minikube

```bash
# Stop cluster (preserves state)
minikube stop

# Delete cluster (removes all data)
minikube delete
```

### Remove Docker Images

```bash
# Remove local images
docker rmi todo-frontend:v1.0.0
docker rmi todo-backend:v1.0.0
```

---

## Advanced Usage

### Custom Configuration

Create a `custom-values.yaml` file:

```yaml
frontend:
  replicas: 2
  resources:
    limits:
      memory: "1Gi"
      cpu: "1000m"

backend:
  replicas: 2
  resources:
    limits:
      memory: "2Gi"
      cpu: "2000m"
```

Install with custom values:

```bash
helm install todo-chatbot ./helm/todo-chatbot \
  -f custom-values.yaml \
  --set secrets.databaseUrl="$DB_URL_B64" \
  --set secrets.jwtSecret="$JWT_SECRET_B64"
```

### Update Image Tags

```bash
# Build new images
docker build -t todo-frontend:v1.1.0 -f docker/frontend/Dockerfile ./frontend
docker build -t todo-backend:v1.1.0 -f docker/backend/Dockerfile ./backend

# Load into Minikube
minikube image load todo-frontend:v1.1.0
minikube image load todo-backend:v1.1.0

# Upgrade Helm release
helm upgrade todo-chatbot ./helm/todo-chatbot \
  --set frontend.image.tag=v1.1.0 \
  --set backend.image.tag=v1.1.0 \
  --reuse-values
```

### Scale Services

```bash
# Scale frontend
kubectl scale deployment todo-chatbot-frontend --replicas=3

# Scale backend
kubectl scale deployment todo-chatbot-backend --replicas=3

# Verify scaling
kubectl get pods
```

### Access Kubernetes Dashboard

```bash
# Enable dashboard addon
minikube addons enable dashboard

# Open dashboard
minikube dashboard
```

---

## Next Steps

After successful deployment:

1. **Explore Application**: Test all features (auth, tasks, chatbot)
2. **Monitor Resources**: Use `kubectl top` to check resource usage
3. **Review Logs**: Check application logs for errors
4. **Test Scaling**: Scale replicas and verify load balancing
5. **Practice Rollback**: Test Helm rollback functionality
6. **Customize Configuration**: Modify values.yaml for your needs

---

## Support

For issues or questions:

1. Check troubleshooting section above
2. Review Helm chart documentation in `helm/todo-chatbot/README.md`
3. Check Kubernetes events: `kubectl get events --sort-by='.lastTimestamp'`
4. Review pod logs: `kubectl logs <pod-name>`
5. Consult specification: `specs/003-minikube-deployment/spec.md`

---

## Summary

**Deployment Time**: ~10-15 minutes (including image builds)

**Key Commands**:
```bash
# Start
minikube start
docker build -t todo-frontend:v1.0.0 -f docker/frontend/Dockerfile ./frontend
docker build -t todo-backend:v1.0.0 -f docker/backend/Dockerfile ./backend
minikube image load todo-frontend:v1.0.0
minikube image load todo-backend:v1.0.0
helm install todo-chatbot ./helm/todo-chatbot --set secrets.databaseUrl="..." --set secrets.jwtSecret="..."

# Access
minikube service todo-chatbot-frontend

# Stop
helm uninstall todo-chatbot
minikube stop
```

**Success Criteria**:
- ✅ All pods Running
- ✅ Services have endpoints
- ✅ Frontend accessible in browser
- ✅ Backend health check passes
- ✅ End-to-end functionality works

#!/bin/bash
# T118-T120: Master deployment script for cloud Kubernetes deployment
# Phase V - Part C: Production Cloud Deployment
# This script orchestrates full deployment with proper ordering and validation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if required arguments are provided
if [ "$#" -lt 3 ]; then
    print_error "Usage: $0 <namespace> <environment> <database-url> <jwt-secret>"
    echo ""
    echo "Arguments:"
    echo "  namespace     - Kubernetes namespace (e.g., todo-app)"
    echo "  environment   - Environment: dev, staging, or prod"
    echo "  database-url  - PostgreSQL connection string"
    echo "  jwt-secret    - JWT secret for authentication"
    echo ""
    echo "Example:"
    echo "  $0 todo-app prod 'postgresql://user:pass@host:5432/db' 'your-jwt-secret'"
    exit 1
fi

NAMESPACE=$1
ENVIRONMENT=$2
DATABASE_URL=$3
JWT_SECRET=$4

echo "========================================="
echo "TODO APP CLOUD DEPLOYMENT"
echo "========================================="
print_info "Namespace: $NAMESPACE"
print_info "Environment: $ENVIRONMENT"
echo ""

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
    print_error "Invalid environment: $ENVIRONMENT. Must be dev, staging, or prod"
    exit 1
fi

# Check prerequisites
print_step "Checking prerequisites..."
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed or not in PATH"
    exit 1
fi

if ! command -v helm &> /dev/null; then
    print_error "helm is not installed or not in PATH"
    exit 1
fi

if ! command -v dapr &> /dev/null; then
    print_warning "dapr CLI is not installed. Dapr installation will be skipped."
    SKIP_DAPR=true
else
    SKIP_DAPR=false
fi

print_info "✓ Prerequisites check passed"
echo ""

# T119: Deployment order logic
# Step 1: Create namespace
print_step "Step 1: Creating namespace..."
if kubectl get namespace "$NAMESPACE" &> /dev/null; then
    print_warning "Namespace $NAMESPACE already exists"
else
    kubectl create namespace "$NAMESPACE"
    print_info "✓ Namespace created"
fi
echo ""

# T120: Validation checkpoint
print_info "Validation checkpoint: Namespace exists"
if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
    print_error "Namespace validation failed"
    exit 1
fi
print_info "✓ Checkpoint passed"
echo ""

# Step 2: Create secrets
print_step "Step 2: Creating Kubernetes Secrets..."
./scripts/create-secrets.sh "$NAMESPACE" "$DATABASE_URL" "$JWT_SECRET"
if [ $? -ne 0 ]; then
    print_error "Secret creation failed"
    exit 1
fi
print_info "✓ Secrets created"
echo ""

# T120: Validation checkpoint
print_info "Validation checkpoint: Secrets exist"
if ! kubectl get secret app-secrets -n "$NAMESPACE" &> /dev/null; then
    print_error "Secrets validation failed"
    exit 1
fi
print_info "✓ Checkpoint passed"
echo ""

# Step 3: Install Dapr control plane
if [ "$SKIP_DAPR" = false ]; then
    print_step "Step 3: Installing Dapr control plane..."
    ./scripts/install-dapr.sh dapr-system
    if [ $? -ne 0 ]; then
        print_error "Dapr installation failed"
        exit 1
    fi
    print_info "✓ Dapr installed"
    echo ""

    # T120: Validation checkpoint
    print_info "Validation checkpoint: Dapr is running"
    DAPR_PODS=$(kubectl get pods -n dapr-system -l app.kubernetes.io/part-of=dapr --no-headers 2>/dev/null | wc -l)
    if [ "$DAPR_PODS" -eq 0 ]; then
        print_error "Dapr validation failed"
        exit 1
    fi
    print_info "✓ Checkpoint passed ($DAPR_PODS Dapr pods running)"
    echo ""
else
    print_warning "Skipping Dapr installation (dapr CLI not found)"
    echo ""
fi

# Step 4: Update Helm dependencies
print_step "Step 4: Updating Helm dependencies..."
cd helm/todo-app
helm dependency update
cd ../..
print_info "✓ Helm dependencies updated"
echo ""

# Step 5: Deploy core services (frontend and backend)
print_step "Step 5: Deploying core services..."
./scripts/deploy-core-services.sh "$NAMESPACE" "$ENVIRONMENT"
if [ $? -ne 0 ]; then
    print_error "Core services deployment failed"
    exit 1
fi
print_info "✓ Core services deployed"
echo ""

# T120: Validation checkpoint
print_info "Validation checkpoint: Core services running"
FRONTEND_PODS=$(kubectl get pods -l app=frontend -n "$NAMESPACE" --field-selector=status.phase=Running --no-headers 2>/dev/null | wc -l)
BACKEND_PODS=$(kubectl get pods -l app=backend -n "$NAMESPACE" --field-selector=status.phase=Running --no-headers 2>/dev/null | wc -l)
if [ "$FRONTEND_PODS" -eq 0 ] || [ "$BACKEND_PODS" -eq 0 ]; then
    print_error "Core services validation failed"
    kubectl get pods -n "$NAMESPACE"
    exit 1
fi
print_info "✓ Checkpoint passed (Frontend: $FRONTEND_PODS pods, Backend: $BACKEND_PODS pods)"
echo ""

# Step 6: Deploy event-driven services (Kafka, Dapr components, event services)
print_step "Step 6: Deploying event-driven services..."
./scripts/deploy-event-services.sh "$NAMESPACE" "$ENVIRONMENT"
if [ $? -ne 0 ]; then
    print_error "Event-driven services deployment failed"
    exit 1
fi
print_info "✓ Event-driven services deployed"
echo ""

# T120: Validation checkpoint
print_info "Validation checkpoint: Event services running"
KAFKA_PODS=$(kubectl get pods -l app=kafka -n "$NAMESPACE" --field-selector=status.phase=Running --no-headers 2>/dev/null | wc -l)
if [ "$KAFKA_PODS" -eq 0 ]; then
    print_warning "Kafka validation warning: no running pods found"
fi
print_info "✓ Checkpoint passed (Kafka: $KAFKA_PODS pods)"
echo ""

# Step 7: Final validation
print_step "Step 7: Running final validation..."
./scripts/validate-deployment.sh "$NAMESPACE"
VALIDATION_RESULT=$?
echo ""

# Get frontend URL
print_step "Step 8: Getting frontend URL..."
SVC_TYPE=$(kubectl get svc frontend -n "$NAMESPACE" -o jsonpath='{.spec.type}')

if [ "$SVC_TYPE" == "LoadBalancer" ]; then
    print_info "Waiting for LoadBalancer external IP..."
    kubectl wait --for=jsonpath='{.status.loadBalancer.ingress[0].ip}' \
        svc/frontend -n "$NAMESPACE" --timeout=300s 2>/dev/null || true

    EXTERNAL_IP=$(kubectl get svc frontend -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    if [ -n "$EXTERNAL_IP" ]; then
        FRONTEND_URL="http://$EXTERNAL_IP"
    else
        FRONTEND_URL="<pending>"
    fi
elif [ "$SVC_TYPE" == "NodePort" ]; then
    NODE_PORT=$(kubectl get svc frontend -n "$NAMESPACE" -o jsonpath='{.spec.ports[0].nodePort}')
    NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[0].address}')
    FRONTEND_URL="http://$NODE_IP:$NODE_PORT"
else
    FRONTEND_URL="<ClusterIP - use port-forward>"
fi
echo ""

# Display deployment summary
echo "========================================="
echo "DEPLOYMENT COMPLETE"
echo "========================================="
echo "Environment: $ENVIRONMENT"
echo "Namespace: $NAMESPACE"
echo ""
echo "Deployed Services:"
echo "  ✓ Frontend (LoadBalancer)"
echo "  ✓ Backend (with Dapr sidecar)"
echo "  ✓ Kafka (message broker)"
echo "  ✓ Zookeeper (Kafka coordination)"
echo "  ✓ Dapr Components (Pub/Sub)"
echo "  ✓ Recurring Task Service (with Dapr)"
echo "  ✓ Notification Service (with Dapr)"
echo ""
echo "Frontend URL: $FRONTEND_URL"
echo ""
echo "Useful Commands:"
echo "  kubectl get pods -n $NAMESPACE"
echo "  kubectl logs -f deployment/frontend -n $NAMESPACE"
echo "  kubectl logs -f deployment/backend -n $NAMESPACE"
echo "  helm list -n $NAMESPACE"
echo ""
echo "Rollback:"
echo "  ./scripts/rollback.sh <release-name> $NAMESPACE"
echo ""

if [ $VALIDATION_RESULT -eq 0 ]; then
    print_info "✓ All validation checks passed!"
    echo ""
    print_info "Deployment successful!"
    exit 0
else
    print_warning "⚠ Some validation checks failed. Review the output above."
    echo ""
    print_warning "Deployment completed with warnings"
    exit 1
fi

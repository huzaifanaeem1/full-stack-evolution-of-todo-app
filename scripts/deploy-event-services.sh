#!/bin/bash
# T084: Deploy event-driven services (Kafka, Dapr components, event services) script
# Phase V - Part C: Production Cloud Deployment
# This script deploys Kafka, Dapr components, and event-driven services to Kubernetes

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Check if required arguments are provided
if [ "$#" -lt 1 ]; then
    print_error "Usage: $0 <namespace> [environment]"
    echo ""
    echo "Arguments:"
    echo "  namespace    - Kubernetes namespace (e.g., todo-app)"
    echo "  environment  - Optional: dev, staging, or prod (default: dev)"
    echo ""
    echo "Example:"
    echo "  $0 todo-app dev"
    exit 1
fi

NAMESPACE=$1
ENVIRONMENT=${2:-dev}

print_info "Deploying event-driven services to namespace: $NAMESPACE"
print_info "Environment: $ENVIRONMENT"
echo ""

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
    print_error "Invalid environment: $ENVIRONMENT. Must be dev, staging, or prod"
    exit 1
fi

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed or not in PATH"
    exit 1
fi

# Check if helm is available
if ! command -v helm &> /dev/null; then
    print_error "helm is not installed or not in PATH"
    exit 1
fi

# Check if namespace exists
if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
    print_warning "Namespace $NAMESPACE does not exist. Creating it..."
    kubectl create namespace "$NAMESPACE"
fi

# Check if Dapr is installed
print_info "Checking if Dapr control plane is installed..."
if ! kubectl get namespace dapr-system &> /dev/null; then
    print_error "Dapr control plane is not installed"
    print_error "Please run ./scripts/install-dapr.sh first"
    exit 1
fi

DAPR_PODS=$(kubectl get pods -n dapr-system -l app.kubernetes.io/part-of=dapr --no-headers 2>/dev/null | wc -l)
if [ "$DAPR_PODS" -eq 0 ]; then
    print_error "Dapr control plane is not running"
    print_error "Please run ./scripts/install-dapr.sh first"
    exit 1
fi
print_info "✓ Dapr control plane is running with $DAPR_PODS pods"
echo ""

# Set values file based on environment
VALUES_FILE="helm/todo-app/values-${ENVIRONMENT}.yaml"
if [ ! -f "$VALUES_FILE" ]; then
    print_error "Values file not found: $VALUES_FILE"
    exit 1
fi

print_info "Using values file: $VALUES_FILE"
echo ""

# Deploy Kafka
print_info "Deploying Kafka..."
helm upgrade --install kafka ./helm/kafka \
    --namespace="$NAMESPACE" \
    --values="$VALUES_FILE" \
    --wait \
    --timeout=5m

if [ $? -eq 0 ]; then
    print_info "✓ Kafka deployed successfully"
else
    print_error "✗ Kafka deployment failed"
    exit 1
fi
echo ""

# Wait for Kafka to be ready
print_info "Waiting for Kafka to be ready..."
kubectl wait --for=condition=ready pod -l app=kafka -n "$NAMESPACE" --timeout=300s

if [ $? -eq 0 ]; then
    print_info "✓ Kafka is ready"
else
    print_warning "⚠ Kafka readiness check timed out. Continuing anyway..."
fi
echo ""

# Deploy Dapr components
print_info "Deploying Dapr components..."
helm upgrade --install dapr-components ./helm/dapr-components \
    --namespace="$NAMESPACE" \
    --values="$VALUES_FILE" \
    --wait \
    --timeout=5m

if [ $? -eq 0 ]; then
    print_info "✓ Dapr components deployed successfully"
else
    print_error "✗ Dapr components deployment failed"
    exit 1
fi
echo ""

# Verify Dapr components
print_info "Verifying Dapr components..."
kubectl get components -n "$NAMESPACE"
echo ""

# Deploy Recurring Task Service
print_info "Deploying Recurring Task Service..."
helm upgrade --install recurring-task-service ./helm/recurring-task-service \
    --namespace="$NAMESPACE" \
    --values="$VALUES_FILE" \
    --wait \
    --timeout=5m

if [ $? -eq 0 ]; then
    print_info "✓ Recurring Task Service deployed successfully"
else
    print_error "✗ Recurring Task Service deployment failed"
    exit 1
fi
echo ""

# Deploy Notification Service
print_info "Deploying Notification Service..."
helm upgrade --install notification-service ./helm/notification-service \
    --namespace="$NAMESPACE" \
    --values="$VALUES_FILE" \
    --wait \
    --timeout=5m

if [ $? -eq 0 ]; then
    print_info "✓ Notification Service deployed successfully"
else
    print_error "✗ Notification Service deployment failed"
    exit 1
fi
echo ""

# Validate deployment
print_info "Validating deployment..."
./scripts/validate-deployment.sh "$NAMESPACE"

if [ $? -eq 0 ]; then
    print_info "✓ Deployment validation passed"
else
    print_warning "⚠ Deployment validation failed. Check the output above for details."
fi
echo ""

# Display deployment status
print_info "Deployment status:"
kubectl get pods -n "$NAMESPACE"
echo ""

print_info "Dapr components:"
kubectl get components -n "$NAMESPACE"
echo ""

# Display next steps
echo "========================================="
echo "EVENT-DRIVEN SERVICES DEPLOYMENT COMPLETE"
echo "========================================="
echo "Deployed services:"
echo "  • Kafka (message broker)"
echo "  • Zookeeper (Kafka coordination)"
echo "  • Dapr Pub/Sub component (pubsub-kafka)"
echo "  • Recurring Task Service (with Dapr sidecar)"
echo "  • Notification Service (with Dapr sidecar)"
echo ""
echo "To check pod status:"
echo "  kubectl get pods -n $NAMESPACE"
echo ""
echo "To view Kafka logs:"
echo "  kubectl logs -f statefulset/kafka -n $NAMESPACE"
echo ""
echo "To view Recurring Task Service logs:"
echo "  kubectl logs -f deployment/recurring-task-service -n $NAMESPACE"
echo "  kubectl logs -f deployment/recurring-task-service -c daprd -n $NAMESPACE  # Dapr sidecar"
echo ""
echo "To view Notification Service logs:"
echo "  kubectl logs -f deployment/notification-service -n $NAMESPACE"
echo "  kubectl logs -f deployment/notification-service -c daprd -n $NAMESPACE  # Dapr sidecar"
echo ""
echo "To test Pub/Sub:"
echo "  kubectl exec -it deployment/backend -n $NAMESPACE -- curl -X POST http://localhost:3500/v1.0/publish/pubsub-kafka/task-events -d '{\"event\":\"test\"}''"
echo ""

print_info "Event-driven services deployment complete!"

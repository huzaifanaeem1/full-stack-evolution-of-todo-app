#!/bin/bash
# T041: Deploy core services (frontend and backend) script
# This script deploys frontend and backend services to Kubernetes

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

print_info "Deploying core services to namespace: $NAMESPACE"
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

# Check if secrets exist
if ! kubectl get secret app-secrets -n "$NAMESPACE" &> /dev/null; then
    print_error "Secret 'app-secrets' does not exist in namespace $NAMESPACE"
    print_error "Please run create-secrets.sh first to create required secrets"
    exit 1
fi

# Set values file based on environment
VALUES_FILE="helm/todo-app/values-${ENVIRONMENT}.yaml"
if [ ! -f "$VALUES_FILE" ]; then
    print_error "Values file not found: $VALUES_FILE"
    exit 1
fi

print_info "Using values file: $VALUES_FILE"
echo ""

# Deploy frontend
print_info "Deploying frontend..."
helm upgrade --install frontend ./helm/frontend \
    --namespace="$NAMESPACE" \
    --values="$VALUES_FILE" \
    --wait \
    --timeout=5m

if [ $? -eq 0 ]; then
    print_info "✓ Frontend deployed successfully"
else
    print_error "✗ Frontend deployment failed"
    exit 1
fi
echo ""

# Deploy backend
print_info "Deploying backend..."
helm upgrade --install backend ./helm/backend \
    --namespace="$NAMESPACE" \
    --values="$VALUES_FILE" \
    --wait \
    --timeout=5m

if [ $? -eq 0 ]; then
    print_info "✓ Backend deployed successfully"
else
    print_error "✗ Backend deployment failed"
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

# Get frontend URL
print_info "Getting frontend URL..."
SVC_TYPE=$(kubectl get svc frontend -n "$NAMESPACE" -o jsonpath='{.spec.type}')

if [ "$SVC_TYPE" == "LoadBalancer" ]; then
    print_info "Waiting for LoadBalancer external IP..."
    kubectl wait --for=jsonpath='{.status.loadBalancer.ingress[0].ip}' \
        svc/frontend -n "$NAMESPACE" --timeout=300s 2>/dev/null || true

    EXTERNAL_IP=$(kubectl get svc frontend -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    if [ -n "$EXTERNAL_IP" ]; then
        echo ""
        echo "========================================="
        echo "DEPLOYMENT COMPLETE"
        echo "========================================="
        echo "Frontend URL: http://$EXTERNAL_IP"
        echo ""
        echo "To check pod status:"
        echo "  kubectl get pods -n $NAMESPACE"
        echo ""
        echo "To view logs:"
        echo "  kubectl logs -f deployment/frontend -n $NAMESPACE"
        echo "  kubectl logs -f deployment/backend -n $NAMESPACE"
    else
        print_warning "LoadBalancer external IP is still pending. Run this to get the IP:"
        echo "  kubectl get svc frontend -n $NAMESPACE"
    fi
elif [ "$SVC_TYPE" == "NodePort" ]; then
    NODE_PORT=$(kubectl get svc frontend -n "$NAMESPACE" -o jsonpath='{.spec.ports[0].nodePort}')
    NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[0].address}')
    echo ""
    echo "========================================="
    echo "DEPLOYMENT COMPLETE"
    echo "========================================="
    echo "Frontend URL: http://$NODE_IP:$NODE_PORT"
    echo ""
fi

print_info "Core services deployment complete!"

#!/bin/bash
# T083: Install Dapr control plane script
# Phase V - Part C: Production Cloud Deployment
# This script installs Dapr control plane to Kubernetes cluster

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
    print_error "Usage: $0 <namespace> [dapr-version]"
    echo ""
    echo "Arguments:"
    echo "  namespace     - Kubernetes namespace for Dapr (e.g., dapr-system)"
    echo "  dapr-version  - Optional: Dapr version to install (default: 1.12.0)"
    echo ""
    echo "Example:"
    echo "  $0 dapr-system 1.12.0"
    exit 1
fi

NAMESPACE=$1
DAPR_VERSION=${2:-1.12.0}

print_info "Installing Dapr control plane"
print_info "Namespace: $NAMESPACE"
print_info "Dapr Version: $DAPR_VERSION"
echo ""

# Check if dapr CLI is available
if ! command -v dapr &> /dev/null; then
    print_error "Dapr CLI is not installed or not in PATH"
    print_info "Install Dapr CLI from: https://docs.dapr.io/getting-started/install-dapr-cli/"
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

# Check if Dapr is already installed
print_info "Checking if Dapr is already installed..."
if kubectl get namespace "$NAMESPACE" &> /dev/null; then
    print_warning "Namespace $NAMESPACE already exists"

    # Check if Dapr control plane is running
    DAPR_PODS=$(kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/part-of=dapr --no-headers 2>/dev/null | wc -l)
    if [ "$DAPR_PODS" -gt 0 ]; then
        print_warning "Dapr control plane is already installed with $DAPR_PODS pods"
        read -p "Do you want to upgrade/reinstall? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Keeping existing Dapr installation. Exiting."
            exit 0
        fi
    fi
fi

# Install Dapr using Helm
print_info "Installing Dapr control plane using Helm..."
print_info "Adding Dapr Helm repository..."
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update

print_info "Installing Dapr to namespace: $NAMESPACE"
helm upgrade --install dapr dapr/dapr \
    --version="$DAPR_VERSION" \
    --namespace="$NAMESPACE" \
    --create-namespace \
    --wait \
    --timeout=5m

if [ $? -eq 0 ]; then
    print_info "✓ Dapr control plane installed successfully"
else
    print_error "✗ Dapr installation failed"
    exit 1
fi
echo ""

# Verify installation
print_info "Verifying Dapr installation..."
kubectl get pods -n "$NAMESPACE"
echo ""

# Check Dapr status
print_info "Checking Dapr status..."
dapr status -k

if [ $? -eq 0 ]; then
    print_info "✓ Dapr is running and healthy"
else
    print_warning "⚠ Dapr status check failed. Check the output above for details."
fi
echo ""

# Display next steps
echo "========================================="
echo "DAPR INSTALLATION COMPLETE"
echo "========================================="
echo "Dapr control plane is installed in namespace: $NAMESPACE"
echo ""
echo "Next steps:"
echo "1. Deploy Dapr components (Pub/Sub, State Store):"
echo "   helm upgrade --install dapr-components ./helm/dapr-components --namespace=todo-app"
echo ""
echo "2. Deploy applications with Dapr sidecars:"
echo "   ./scripts/deploy-event-services.sh todo-app dev"
echo ""
echo "To check Dapr status:"
echo "  dapr status -k"
echo ""
echo "To view Dapr logs:"
echo "  kubectl logs -l app.kubernetes.io/part-of=dapr -n $NAMESPACE"
echo ""

print_info "Dapr installation complete!"

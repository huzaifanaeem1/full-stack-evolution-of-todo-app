#!/bin/bash
# T116: Helm rollback automation script
# Phase V - Part C: Production Cloud Deployment
# This script automates Helm rollback for failed deployments

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
if [ "$#" -lt 2 ]; then
    print_error "Usage: $0 <release-name> <namespace> [revision]"
    echo ""
    echo "Arguments:"
    echo "  release-name - Helm release name (e.g., frontend, backend, todo-app)"
    echo "  namespace    - Kubernetes namespace (e.g., todo-app)"
    echo "  revision     - Optional: specific revision to rollback to (default: previous)"
    echo ""
    echo "Examples:"
    echo "  $0 frontend todo-app           # Rollback to previous revision"
    echo "  $0 backend todo-app 5          # Rollback to revision 5"
    echo "  $0 todo-app todo-app           # Rollback entire umbrella chart"
    exit 1
fi

RELEASE_NAME=$1
NAMESPACE=$2
REVISION=${3:-}

print_info "Helm Rollback Automation"
print_info "Release: $RELEASE_NAME"
print_info "Namespace: $NAMESPACE"
echo ""

# Check if helm is available
if ! command -v helm &> /dev/null; then
    print_error "helm is not installed or not in PATH"
    exit 1
fi

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed or not in PATH"
    exit 1
fi

# Check if namespace exists
if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
    print_error "Namespace $NAMESPACE does not exist"
    exit 1
fi

# Check if release exists
print_info "Checking if release exists..."
if ! helm list -n "$NAMESPACE" | grep -q "^$RELEASE_NAME"; then
    print_error "Release $RELEASE_NAME not found in namespace $NAMESPACE"
    print_info "Available releases:"
    helm list -n "$NAMESPACE"
    exit 1
fi

# Show release history
print_info "Release history:"
helm history "$RELEASE_NAME" -n "$NAMESPACE"
echo ""

# Get current revision
CURRENT_REVISION=$(helm list -n "$NAMESPACE" -o json | jq -r ".[] | select(.name==\"$RELEASE_NAME\") | .revision")
print_info "Current revision: $CURRENT_REVISION"

# Determine target revision
if [ -z "$REVISION" ]; then
    # Rollback to previous revision
    TARGET_REVISION=$((CURRENT_REVISION - 1))
    if [ "$TARGET_REVISION" -lt 1 ]; then
        print_error "Cannot rollback: no previous revision available"
        exit 1
    fi
    print_info "Target revision: $TARGET_REVISION (previous)"
else
    # Rollback to specific revision
    TARGET_REVISION=$REVISION
    print_info "Target revision: $TARGET_REVISION (specified)"
fi
echo ""

# Confirm rollback
print_warning "This will rollback $RELEASE_NAME from revision $CURRENT_REVISION to revision $TARGET_REVISION"
read -p "Do you want to proceed? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_info "Rollback cancelled"
    exit 0
fi
echo ""

# Perform rollback
print_info "Rolling back $RELEASE_NAME to revision $TARGET_REVISION..."
if [ -z "$REVISION" ]; then
    # Rollback to previous (no revision specified)
    helm rollback "$RELEASE_NAME" -n "$NAMESPACE" --wait --timeout=5m
else
    # Rollback to specific revision
    helm rollback "$RELEASE_NAME" "$TARGET_REVISION" -n "$NAMESPACE" --wait --timeout=5m
fi

if [ $? -eq 0 ]; then
    print_info "✓ Rollback completed successfully"
else
    print_error "✗ Rollback failed"
    exit 1
fi
echo ""

# Verify rollback
print_info "Verifying rollback..."
NEW_REVISION=$(helm list -n "$NAMESPACE" -o json | jq -r ".[] | select(.name==\"$RELEASE_NAME\") | .revision")
print_info "New revision: $NEW_REVISION"
echo ""

# Check pod status
print_info "Checking pod status..."
case "$RELEASE_NAME" in
    "frontend")
        kubectl get pods -l app=frontend -n "$NAMESPACE"
        ;;
    "backend")
        kubectl get pods -l app=backend -n "$NAMESPACE"
        ;;
    "kafka")
        kubectl get pods -l app=kafka -n "$NAMESPACE"
        ;;
    "recurring-task-service")
        kubectl get pods -l app=recurring-task-service -n "$NAMESPACE"
        ;;
    "notification-service")
        kubectl get pods -l app=notification-service -n "$NAMESPACE"
        ;;
    "todo-app")
        kubectl get pods -n "$NAMESPACE"
        ;;
    *)
        kubectl get pods -l app.kubernetes.io/instance="$RELEASE_NAME" -n "$NAMESPACE"
        ;;
esac
echo ""

# Run validation
print_info "Running deployment validation..."
if [ -f "./scripts/validate-deployment.sh" ]; then
    ./scripts/validate-deployment.sh "$NAMESPACE"
    if [ $? -eq 0 ]; then
        print_info "✓ Validation passed"
    else
        print_warning "⚠ Validation failed. Check the output above for details."
    fi
else
    print_warning "Validation script not found. Skipping validation."
fi
echo ""

# Display rollback summary
echo "========================================="
echo "ROLLBACK COMPLETE"
echo "========================================="
echo "Release: $RELEASE_NAME"
echo "Namespace: $NAMESPACE"
echo "Previous revision: $CURRENT_REVISION"
echo "Current revision: $NEW_REVISION"
echo ""
echo "To view release history:"
echo "  helm history $RELEASE_NAME -n $NAMESPACE"
echo ""
echo "To view pod logs:"
echo "  kubectl logs -l app=$RELEASE_NAME -n $NAMESPACE"
echo ""
echo "To check release status:"
echo "  helm status $RELEASE_NAME -n $NAMESPACE"
echo ""

print_info "Rollback complete!"

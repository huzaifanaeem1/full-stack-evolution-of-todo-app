#!/bin/bash
# T039: Create Kubernetes Secrets script
# This script creates Kubernetes Secrets for the Todo application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
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
    print_error "Usage: $0 <namespace> <database-url> <jwt-secret>"
    echo ""
    echo "Example:"
    echo "  $0 todo-app 'postgresql://user:pass@host:5432/db' 'your-jwt-secret'"
    exit 1
fi

NAMESPACE=$1
DATABASE_URL=$2
JWT_SECRET=$3

print_info "Creating Kubernetes Secrets in namespace: $NAMESPACE"

# Check if namespace exists
if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
    print_warning "Namespace $NAMESPACE does not exist. Creating it..."
    kubectl create namespace "$NAMESPACE"
fi

# Check if secret already exists
if kubectl get secret app-secrets -n "$NAMESPACE" &> /dev/null; then
    print_warning "Secret 'app-secrets' already exists in namespace $NAMESPACE"
    read -p "Do you want to delete and recreate it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kubectl delete secret app-secrets -n "$NAMESPACE"
        print_info "Deleted existing secret"
    else
        print_info "Keeping existing secret. Exiting."
        exit 0
    fi
fi

# Create the secret
print_info "Creating secret 'app-secrets'..."
kubectl create secret generic app-secrets \
    --from-literal=DATABASE_URL="$DATABASE_URL" \
    --from-literal=JWT_SECRET="$JWT_SECRET" \
    --namespace="$NAMESPACE"

# Verify secret was created
if kubectl get secret app-secrets -n "$NAMESPACE" &> /dev/null; then
    print_info "✓ Secret 'app-secrets' created successfully"

    # Show secret details (without values)
    print_info "Secret details:"
    kubectl describe secret app-secrets -n "$NAMESPACE"
else
    print_error "✗ Failed to create secret"
    exit 1
fi

print_info "Secret creation complete!"
print_warning "Remember: Never commit secrets to version control"

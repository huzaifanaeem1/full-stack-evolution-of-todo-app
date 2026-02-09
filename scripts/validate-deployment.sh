#!/bin/bash
# T040: Post-deployment validation script
# This script validates the deployment of Todo application services

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

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_fail() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check if namespace argument is provided
if [ "$#" -lt 1 ]; then
    print_error "Usage: $0 <namespace>"
    echo ""
    echo "Example:"
    echo "  $0 todo-app"
    exit 1
fi

NAMESPACE=$1
FAILED_CHECKS=0

print_info "Validating deployment in namespace: $NAMESPACE"
echo ""

# Check 1: Namespace exists
print_info "Check 1: Namespace exists"
if kubectl get namespace "$NAMESPACE" &> /dev/null; then
    print_success "Namespace $NAMESPACE exists"
else
    print_fail "Namespace $NAMESPACE does not exist"
    ((FAILED_CHECKS++))
fi
echo ""

# Check 2: All pods are running
print_info "Check 2: All pods are running"
PODS=$(kubectl get pods -n "$NAMESPACE" --no-headers 2>/dev/null | wc -l)
RUNNING_PODS=$(kubectl get pods -n "$NAMESPACE" --field-selector=status.phase=Running --no-headers 2>/dev/null | wc -l)

if [ "$PODS" -eq 0 ]; then
    print_fail "No pods found in namespace $NAMESPACE"
    ((FAILED_CHECKS++))
elif [ "$PODS" -eq "$RUNNING_PODS" ]; then
    print_success "All $PODS pods are running"
else
    print_fail "$RUNNING_PODS/$PODS pods are running"
    kubectl get pods -n "$NAMESPACE"
    ((FAILED_CHECKS++))
fi
echo ""

# Check 3: Dapr sidecars are injected
print_info "Check 3: Dapr sidecars are injected (backend services)"
DAPR_PODS=$(kubectl get pods -n "$NAMESPACE" -l dapr.io/enabled=true --no-headers 2>/dev/null | wc -l)
if [ "$DAPR_PODS" -gt 0 ]; then
    print_success "Found $DAPR_PODS pods with Dapr sidecars"
    # Check if they have 2 containers (app + daprd)
    kubectl get pods -n "$NAMESPACE" -l dapr.io/enabled=true -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.containerStatuses[*].name}{"\n"}{end}'
else
    print_warning "No pods with Dapr sidecars found (expected for backend services)"
fi
echo ""

# Check 4: Services have endpoints
print_info "Check 4: Services have endpoints"
SERVICES=$(kubectl get svc -n "$NAMESPACE" --no-headers 2>/dev/null | awk '{print $1}')
for svc in $SERVICES; do
    ENDPOINTS=$(kubectl get endpoints "$svc" -n "$NAMESPACE" -o jsonpath='{.subsets[*].addresses[*].ip}' 2>/dev/null)
    if [ -n "$ENDPOINTS" ]; then
        print_success "Service $svc has endpoints"
    else
        print_fail "Service $svc has no endpoints"
        ((FAILED_CHECKS++))
    fi
done
echo ""

# Check 5: Secrets exist
print_info "Check 5: Secrets exist"
if kubectl get secret app-secrets -n "$NAMESPACE" &> /dev/null; then
    print_success "Secret 'app-secrets' exists"
else
    print_fail "Secret 'app-secrets' does not exist"
    ((FAILED_CHECKS++))
fi
echo ""

# Check 6: Frontend service has external IP (if LoadBalancer)
print_info "Check 6: Frontend service accessibility"
if kubectl get svc frontend -n "$NAMESPACE" &> /dev/null; then
    SVC_TYPE=$(kubectl get svc frontend -n "$NAMESPACE" -o jsonpath='{.spec.type}')
    if [ "$SVC_TYPE" == "LoadBalancer" ]; then
        EXTERNAL_IP=$(kubectl get svc frontend -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
        if [ -n "$EXTERNAL_IP" ]; then
            print_success "Frontend LoadBalancer has external IP: $EXTERNAL_IP"
        else
            print_warning "Frontend LoadBalancer external IP is pending (may take a few minutes)"
        fi
    else
        print_success "Frontend service type: $SVC_TYPE"
    fi
else
    print_fail "Frontend service not found"
    ((FAILED_CHECKS++))
fi
echo ""

# Check 7: Dapr components (if deployed)
print_info "Check 7: Dapr components"
COMPONENTS=$(kubectl get components -n "$NAMESPACE" --no-headers 2>/dev/null | wc -l)
if [ "$COMPONENTS" -gt 0 ]; then
    print_success "Found $COMPONENTS Dapr component(s)"
    kubectl get components -n "$NAMESPACE"
else
    print_warning "No Dapr components found (expected if event-driven services not deployed yet)"
fi
echo ""

# Check 8: Resource limits are configured (T117)
print_info "Check 8: Resource limits configured"
DEPLOYMENTS=$(kubectl get deployments -n "$NAMESPACE" --no-headers 2>/dev/null | awk '{print $1}')
MISSING_RESOURCES=0
for deploy in $DEPLOYMENTS; do
    # Check if deployment has resource requests and limits
    RESOURCES=$(kubectl get deployment "$deploy" -n "$NAMESPACE" -o jsonpath='{.spec.template.spec.containers[0].resources}' 2>/dev/null)
    if [ -z "$RESOURCES" ] || [ "$RESOURCES" == "{}" ]; then
        print_fail "Deployment $deploy has no resource limits configured"
        ((MISSING_RESOURCES++))
        ((FAILED_CHECKS++))
    else
        # Check if both requests and limits are present
        REQUESTS=$(kubectl get deployment "$deploy" -n "$NAMESPACE" -o jsonpath='{.spec.template.spec.containers[0].resources.requests}' 2>/dev/null)
        LIMITS=$(kubectl get deployment "$deploy" -n "$NAMESPACE" -o jsonpath='{.spec.template.spec.containers[0].resources.limits}' 2>/dev/null)
        if [ -z "$REQUESTS" ] || [ "$REQUESTS" == "{}" ]; then
            print_fail "Deployment $deploy has no resource requests"
            ((MISSING_RESOURCES++))
            ((FAILED_CHECKS++))
        elif [ -z "$LIMITS" ] || [ "$LIMITS" == "{}" ]; then
            print_fail "Deployment $deploy has no resource limits"
            ((MISSING_RESOURCES++))
            ((FAILED_CHECKS++))
        else
            print_success "Deployment $deploy has resource limits configured"
        fi
    fi
done
if [ "$MISSING_RESOURCES" -eq 0 ]; then
    print_success "All deployments have resource limits configured"
fi
echo ""

# Check 9: Health probes are configured (T117)
print_info "Check 9: Health probes configured"
MISSING_PROBES=0
for deploy in $DEPLOYMENTS; do
    # Check liveness probe
    LIVENESS=$(kubectl get deployment "$deploy" -n "$NAMESPACE" -o jsonpath='{.spec.template.spec.containers[0].livenessProbe}' 2>/dev/null)
    # Check readiness probe
    READINESS=$(kubectl get deployment "$deploy" -n "$NAMESPACE" -o jsonpath='{.spec.template.spec.containers[0].readinessProbe}' 2>/dev/null)

    if [ -z "$LIVENESS" ] || [ "$LIVENESS" == "{}" ]; then
        print_fail "Deployment $deploy has no liveness probe"
        ((MISSING_PROBES++))
        ((FAILED_CHECKS++))
    elif [ -z "$READINESS" ] || [ "$READINESS" == "{}" ]; then
        print_fail "Deployment $deploy has no readiness probe"
        ((MISSING_PROBES++))
        ((FAILED_CHECKS++))
    else
        print_success "Deployment $deploy has health probes configured"
    fi
done
if [ "$MISSING_PROBES" -eq 0 ]; then
    print_success "All deployments have health probes configured"
fi
echo ""

# Summary
echo "========================================="
echo "VALIDATION SUMMARY"
echo "========================================="
if [ "$FAILED_CHECKS" -eq 0 ]; then
    print_success "All validation checks passed!"
    exit 0
else
    print_fail "$FAILED_CHECKS validation check(s) failed"
    exit 1
fi

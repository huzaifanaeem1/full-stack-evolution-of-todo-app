#!/bin/bash
# T132: Post-deployment smoke test script
# Phase V - Part C: Production Cloud Deployment
# This script performs basic smoke tests to verify deployment functionality

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
FAILED_TESTS=0

echo "========================================="
echo "SMOKE TESTS"
echo "========================================="
print_info "Running smoke tests for namespace: $NAMESPACE"
echo ""

# Test 1: Frontend is accessible
print_info "Test 1: Frontend accessibility"
SVC_TYPE=$(kubectl get svc frontend -n "$NAMESPACE" -o jsonpath='{.spec.type}' 2>/dev/null)

if [ -z "$SVC_TYPE" ]; then
    print_fail "Frontend service not found"
    ((FAILED_TESTS++))
else
    if [ "$SVC_TYPE" == "LoadBalancer" ]; then
        EXTERNAL_IP=$(kubectl get svc frontend -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)
        if [ -n "$EXTERNAL_IP" ]; then
            # Test HTTP connectivity
            HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://$EXTERNAL_IP" --connect-timeout 5 || echo "000")
            if [ "$HTTP_CODE" == "200" ] || [ "$HTTP_CODE" == "301" ] || [ "$HTTP_CODE" == "302" ]; then
                print_success "Frontend is accessible at http://$EXTERNAL_IP (HTTP $HTTP_CODE)"
            else
                print_fail "Frontend returned HTTP $HTTP_CODE"
                ((FAILED_TESTS++))
            fi
        else
            print_warning "Frontend LoadBalancer IP is pending"
        fi
    elif [ "$SVC_TYPE" == "NodePort" ]; then
        NODE_PORT=$(kubectl get svc frontend -n "$NAMESPACE" -o jsonpath='{.spec.ports[0].nodePort}')
        print_success "Frontend is accessible via NodePort: $NODE_PORT"
    else
        print_success "Frontend service exists (type: $SVC_TYPE)"
    fi
fi
echo ""

# Test 2: Backend health check
print_info "Test 2: Backend health check"
BACKEND_POD=$(kubectl get pods -l app=backend -n "$NAMESPACE" --field-selector=status.phase=Running -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

if [ -z "$BACKEND_POD" ]; then
    print_fail "No running backend pod found"
    ((FAILED_TESTS++))
else
    # Test health endpoint
    HEALTH_RESPONSE=$(kubectl exec "$BACKEND_POD" -n "$NAMESPACE" -- curl -s http://localhost:8000/health 2>/dev/null || echo "error")
    if [[ "$HEALTH_RESPONSE" == *"ok"* ]] || [[ "$HEALTH_RESPONSE" == *"healthy"* ]] || [[ "$HEALTH_RESPONSE" == *"status"* ]]; then
        print_success "Backend health check passed"
    else
        print_fail "Backend health check failed: $HEALTH_RESPONSE"
        ((FAILED_TESTS++))
    fi
fi
echo ""

# Test 3: Dapr sidecar connectivity
print_info "Test 3: Dapr sidecar connectivity"
if [ -n "$BACKEND_POD" ]; then
    # Check if Dapr sidecar is running
    DAPR_CONTAINER=$(kubectl get pod "$BACKEND_POD" -n "$NAMESPACE" -o jsonpath='{.spec.containers[?(@.name=="daprd")].name}' 2>/dev/null)
    if [ -n "$DAPR_CONTAINER" ]; then
        # Test Dapr health endpoint
        DAPR_HEALTH=$(kubectl exec "$BACKEND_POD" -c daprd -n "$NAMESPACE" -- curl -s http://localhost:3500/v1.0/healthz 2>/dev/null || echo "error")
        if [ "$DAPR_HEALTH" == "true" ] || [[ "$DAPR_HEALTH" == *"ok"* ]]; then
            print_success "Dapr sidecar is healthy"
        else
            print_fail "Dapr sidecar health check failed"
            ((FAILED_TESTS++))
        fi
    else
        print_warning "Dapr sidecar not found (may not be enabled)"
    fi
else
    print_warning "Skipping Dapr test (no backend pod)"
fi
echo ""

# Test 4: Kafka connectivity
print_info "Test 4: Kafka connectivity"
KAFKA_POD=$(kubectl get pods -l app=kafka -n "$NAMESPACE" --field-selector=status.phase=Running -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

if [ -z "$KAFKA_POD" ]; then
    print_warning "No running Kafka pod found (may not be deployed)"
else
    # Test Kafka broker connectivity
    KAFKA_TEST=$(kubectl exec "$KAFKA_POD" -n "$NAMESPACE" -- kafka-broker-api-versions --bootstrap-server localhost:9092 2>/dev/null | grep -c "ApiVersion" || echo "0")
    if [ "$KAFKA_TEST" -gt 0 ]; then
        print_success "Kafka broker is accessible"
    else
        print_fail "Kafka broker connectivity test failed"
        ((FAILED_TESTS++))
    fi
fi
echo ""

# Test 5: Database connectivity (via backend)
print_info "Test 5: Database connectivity"
if [ -n "$BACKEND_POD" ]; then
    # Try to access a backend endpoint that requires database
    DB_TEST=$(kubectl exec "$BACKEND_POD" -n "$NAMESPACE" -- curl -s http://localhost:8000/api/tasks --connect-timeout 5 2>/dev/null || echo "error")
    if [[ "$DB_TEST" != "error" ]] && [[ "$DB_TEST" != *"Connection refused"* ]]; then
        print_success "Database connectivity via backend works"
    else
        print_fail "Database connectivity test failed"
        ((FAILED_TESTS++))
    fi
else
    print_warning "Skipping database test (no backend pod)"
fi
echo ""

# Test 6: Dapr Pub/Sub component
print_info "Test 6: Dapr Pub/Sub component"
PUBSUB_COMPONENT=$(kubectl get component pubsub-kafka -n "$NAMESPACE" -o jsonpath='{.metadata.name}' 2>/dev/null)

if [ -z "$PUBSUB_COMPONENT" ]; then
    print_warning "Dapr Pub/Sub component not found (may not be deployed)"
else
    print_success "Dapr Pub/Sub component exists"

    # Test publishing a message (if backend pod available)
    if [ -n "$BACKEND_POD" ]; then
        PUBLISH_TEST=$(kubectl exec "$BACKEND_POD" -n "$NAMESPACE" -- curl -s -X POST \
            http://localhost:3500/v1.0/publish/pubsub-kafka/test-topic \
            -H "Content-Type: application/json" \
            -d '{"test":"smoke-test"}' 2>/dev/null || echo "error")

        if [[ "$PUBLISH_TEST" != "error" ]]; then
            print_success "Pub/Sub publish test passed"
        else
            print_fail "Pub/Sub publish test failed"
            ((FAILED_TESTS++))
        fi
    fi
fi
echo ""

# Test 7: Recurring Task Service
print_info "Test 7: Recurring Task Service"
RTS_POD=$(kubectl get pods -l app=recurring-task-service -n "$NAMESPACE" --field-selector=status.phase=Running -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

if [ -z "$RTS_POD" ]; then
    print_warning "Recurring Task Service not found (may not be deployed)"
else
    # Test health endpoint
    RTS_HEALTH=$(kubectl exec "$RTS_POD" -n "$NAMESPACE" -- curl -s http://localhost:8001/health 2>/dev/null || echo "error")
    if [[ "$RTS_HEALTH" == *"ok"* ]] || [[ "$RTS_HEALTH" == *"healthy"* ]]; then
        print_success "Recurring Task Service is healthy"
    else
        print_fail "Recurring Task Service health check failed"
        ((FAILED_TESTS++))
    fi
fi
echo ""

# Test 8: Notification Service
print_info "Test 8: Notification Service"
NS_POD=$(kubectl get pods -l app=notification-service -n "$NAMESPACE" --field-selector=status.phase=Running -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

if [ -z "$NS_POD" ]; then
    print_warning "Notification Service not found (may not be deployed)"
else
    # Test health endpoint
    NS_HEALTH=$(kubectl exec "$NS_POD" -n "$NAMESPACE" -- curl -s http://localhost:8002/health 2>/dev/null || echo "error")
    if [[ "$NS_HEALTH" == *"ok"* ]] || [[ "$NS_HEALTH" == *"healthy"* ]]; then
        print_success "Notification Service is healthy"
    else
        print_fail "Notification Service health check failed"
        ((FAILED_TESTS++))
    fi
fi
echo ""

# Summary
echo "========================================="
echo "SMOKE TEST SUMMARY"
echo "========================================="
if [ "$FAILED_TESTS" -eq 0 ]; then
    print_success "All smoke tests passed!"
    echo ""
    print_info "Deployment is functional and ready for use"
    exit 0
else
    print_fail "$FAILED_TESTS smoke test(s) failed"
    echo ""
    print_warning "Some services may not be fully functional. Review the output above."
    exit 1
fi

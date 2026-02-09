# T094-T096: Quickstart Guide for Event-Driven Architecture
# Phase V - Part B: Event-Driven Architecture with Kafka and Dapr

## Quickstart Guide: Event-Driven Architecture with Kafka and Dapr

This guide provides step-by-step instructions for setting up and testing the event-driven Todo system locally and in Minikube.

---

## Prerequisites

- Docker Desktop installed and running
- Minikube installed (`minikube version`)
- Dapr CLI installed (`dapr version`)
- kubectl installed (`kubectl version`)
- Python 3.11+ for local development
- Git for cloning the repository

---

## Architecture Overview

The event-driven architecture consists of:

1. **Chat API Service** (Producer): Publishes task lifecycle events (created, updated, completed, deleted)
2. **Recurring Task Service** (Consumer): Consumes task.completed events and creates next recurring task instances
3. **Notification Service** (Consumer): Consumes reminder events and logs notifications to console
4. **Kafka**: Message broker for event streaming
5. **Dapr**: Infrastructure abstraction layer for Pub/Sub

**Event Flow**:
```
User → Chat API Service → Kafka (via Dapr) → Consumer Services
                            ↓
                      task-events topic
                      reminders topic
```

---

## Local Development Setup

### Step 1: Install Dapr CLI

```bash
# Install Dapr CLI (Windows)
powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"

# Install Dapr CLI (macOS/Linux)
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Verify installation
dapr version
```

### Step 2: Initialize Dapr for Local Development

```bash
# Initialize Dapr (installs Redis, Zipkin containers)
dapr init

# Verify Dapr is running
dapr --version
docker ps  # Should see dapr_redis and dapr_zipkin containers
```

### Step 3: Start Kafka Locally

```bash
# Create docker-compose.yml for Kafka
cat > docker-compose-kafka.yml <<EOF
version: '3'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    ports:
      - "2181:2181"

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
EOF

# Start Kafka
docker-compose -f docker-compose-kafka.yml up -d

# Verify Kafka is running
docker ps | grep kafka
```

### Step 4: Configure Dapr Pub/Sub Component

```bash
# Create Dapr components directory
mkdir -p ~/.dapr/components

# Copy Kafka Pub/Sub component
cp dapr/components/pubsub-kafka.yaml ~/.dapr/components/

# Update broker address for local development
# Edit ~/.dapr/components/pubsub-kafka.yaml
# Change brokers from "kafka:9092" to "localhost:9092"
```

### Step 5: Start Chat API Service with Dapr

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Start with Dapr sidecar
dapr run --app-id chat-api-service --app-port 8000 --dapr-http-port 3500 \
  -- uvicorn src.main:app --host 0.0.0.0 --port 8000

# Verify service is running
curl http://localhost:8000/health
```

### Step 6: Start Recurring Task Service with Dapr

```bash
# Open new terminal
cd recurring-task-service

# Install dependencies
pip install -r requirements.txt

# Set DATABASE_URL environment variable
export DATABASE_URL="your_database_url_here"

# Start with Dapr sidecar
dapr run --app-id recurring-task-service --app-port 8001 --dapr-http-port 3501 \
  -- uvicorn src.main:app --host 0.0.0.0 --port 8001

# Verify service is running
curl http://localhost:8001/health

# Check Dapr subscription
curl http://localhost:8001/dapr/subscribe
```

### Step 7: Start Notification Service with Dapr

```bash
# Open new terminal
cd notification-service

# Install dependencies
pip install -r requirements.txt

# Start with Dapr sidecar
dapr run --app-id notification-service --app-port 8002 --dapr-http-port 3502 \
  -- uvicorn src.main:app --host 0.0.0.0 --port 8002

# Verify service is running
curl http://localhost:8002/health

# Check Dapr subscription
curl http://localhost:8002/dapr/subscribe
```

### Step 8: Test Event Flow

```bash
# Create a recurring task via Chat API Service
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "title": "Daily standup",
    "description": "Team standup meeting",
    "priority": "high",
    "due_date": "2026-02-10",
    "is_recurring": true,
    "recurrence_frequency": "daily"
  }'

# Complete the task
curl -X PATCH http://localhost:8000/api/tasks/{task_id} \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"is_completed": true}'

# Check Recurring Task Service logs for next instance creation
# Check Kafka topic for events
docker exec -it kafka kafka-console-consumer --bootstrap-server localhost:9092 \
  --topic task-events --from-beginning
```

---

## Minikube Deployment

### Step 1: Start Minikube

```bash
# Start Minikube with sufficient resources
minikube start --cpus=4 --memory=8192 --driver=docker

# Verify Minikube is running
minikube status
kubectl cluster-info
```

### Step 2: Install Dapr in Minikube

```bash
# Initialize Dapr in Kubernetes mode
dapr init -k

# Verify Dapr installation
dapr status -k

# Should see dapr-operator, dapr-sidecar-injector, dapr-sentry, dapr-placement
kubectl get pods -n dapr-system
```

### Step 3: Deploy Kafka and Zookeeper

```bash
# Apply Kafka manifests
kubectl apply -f kubernetes/kafka/zookeeper-deployment.yaml
kubectl apply -f kubernetes/kafka/zookeeper-service.yaml
kubectl apply -f kubernetes/kafka/kafka-deployment.yaml
kubectl apply -f kubernetes/kafka/kafka-service.yaml

# Wait for Kafka to be ready
kubectl wait --for=condition=ready pod -l app=kafka --timeout=300s
kubectl wait --for=condition=ready pod -l app=zookeeper --timeout=300s

# Verify Kafka is running
kubectl get pods | grep kafka
kubectl get svc | grep kafka
```

### Step 4: Apply Dapr Pub/Sub Component

```bash
# Apply Dapr component configuration
kubectl apply -f dapr/components/pubsub-kafka.yaml

# Verify component is loaded
kubectl get components
```

### Step 5: Deploy Chat API Service

```bash
# Build and load Docker image into Minikube
cd backend
docker build -t chat-api-service:latest .
minikube image load chat-api-service:latest

# Deploy using Helm (with Dapr annotations already added)
helm upgrade --install todo-chatbot ./helm/todo-chatbot

# Verify deployment
kubectl get pods | grep backend
kubectl logs -f deployment/todo-chatbot-backend -c daprd  # Dapr sidecar logs
kubectl logs -f deployment/todo-chatbot-backend -c backend  # App logs
```

### Step 6: Deploy Recurring Task Service

```bash
# Build and load Docker image
cd recurring-task-service
docker build -t recurring-task-service:latest .
minikube image load recurring-task-service:latest

# Deploy to Kubernetes
kubectl apply -f kubernetes/recurring-task-service/deployment.yaml
kubectl apply -f kubernetes/recurring-task-service/service.yaml

# Verify deployment
kubectl get pods | grep recurring-task-service
kubectl logs -f deployment/recurring-task-service -c recurring-task-service
```

### Step 7: Deploy Notification Service

```bash
# Build and load Docker image
cd notification-service
docker build -t notification-service:latest .
minikube image load notification-service:latest

# Deploy to Kubernetes
kubectl apply -f kubernetes/notification-service/deployment.yaml
kubectl apply -f kubernetes/notification-service/service.yaml

# Verify deployment
kubectl get pods | grep notification-service
kubectl logs -f deployment/notification-service -c notification-service
```

### Step 8: Verify Event Flow in Minikube

```bash
# Port-forward Chat API Service
kubectl port-forward svc/todo-chatbot-backend 8000:8000

# Create and complete a recurring task (same as local testing)
# Check consumer service logs
kubectl logs -f deployment/recurring-task-service -c recurring-task-service
kubectl logs -f deployment/notification-service -c notification-service

# Inspect Kafka topics
kubectl exec -it deployment/kafka -- kafka-topics --list --bootstrap-server localhost:9092
kubectl exec -it deployment/kafka -- kafka-console-consumer --bootstrap-server localhost:9092 \
  --topic task-events --from-beginning
```

---

## Troubleshooting

### Dapr Sidecar Not Injecting

**Symptom**: Pods don't have Dapr sidecar container

**Solution**:
```bash
# Verify Dapr is installed
dapr status -k

# Check sidecar injector
kubectl get pods -n dapr-system | grep sidecar-injector

# Verify annotations in deployment
kubectl describe pod <pod-name> | grep dapr.io
```

### Kafka Connection Errors

**Symptom**: "Failed to connect to Kafka broker"

**Solution**:
```bash
# Verify Kafka is running
kubectl get pods | grep kafka

# Check Kafka logs
kubectl logs deployment/kafka

# Test Kafka connectivity from a pod
kubectl run -it --rm debug --image=confluentinc/cp-kafka:7.5.0 --restart=Never \
  -- kafka-broker-api-versions --bootstrap-server kafka:9092
```

### Events Not Being Published

**Symptom**: No events in Kafka topic

**Solution**:
```bash
# Check Chat API Service logs
kubectl logs deployment/todo-chatbot-backend -c backend | grep "Event published"

# Check Dapr sidecar logs
kubectl logs deployment/todo-chatbot-backend -c daprd

# Verify Dapr component is loaded
kubectl get components
kubectl describe component pubsub-kafka
```

### Consumer Not Receiving Events

**Symptom**: Consumer service not processing events

**Solution**:
```bash
# Check consumer logs
kubectl logs deployment/recurring-task-service -c recurring-task-service

# Verify Dapr subscription
kubectl logs deployment/recurring-task-service -c daprd | grep subscribe

# Check consumer group lag
kubectl exec -it deployment/kafka -- kafka-consumer-groups --bootstrap-server localhost:9092 \
  --describe --group dapr-consumer-group
```

---

## Monitoring and Debugging

### View All Service Logs

```bash
# Chat API Service
kubectl logs -f deployment/todo-chatbot-backend -c backend

# Recurring Task Service
kubectl logs -f deployment/recurring-task-service -c recurring-task-service

# Notification Service
kubectl logs -f deployment/notification-service -c notification-service

# Dapr sidecars
kubectl logs -f deployment/todo-chatbot-backend -c daprd
```

### Inspect Kafka Topics

```bash
# List all topics
kubectl exec -it deployment/kafka -- kafka-topics --list --bootstrap-server localhost:9092

# Describe topic
kubectl exec -it deployment/kafka -- kafka-topics --describe --topic task-events \
  --bootstrap-server localhost:9092

# Consume events from beginning
kubectl exec -it deployment/kafka -- kafka-console-consumer --bootstrap-server localhost:9092 \
  --topic task-events --from-beginning --max-messages 10
```

### Check Dapr Components

```bash
# List components
kubectl get components

# Describe component
kubectl describe component pubsub-kafka

# Check component logs
kubectl logs -n dapr-system deployment/dapr-operator
```

---

## Clean Up

### Local Development

```bash
# Stop Dapr services
dapr stop --app-id chat-api-service
dapr stop --app-id recurring-task-service
dapr stop --app-id notification-service

# Stop Kafka
docker-compose -f docker-compose-kafka.yml down

# Uninstall Dapr (optional)
dapr uninstall
```

### Minikube

```bash
# Delete deployments
kubectl delete -f kubernetes/notification-service/
kubectl delete -f kubernetes/recurring-task-service/
kubectl delete -f kubernetes/kafka/
helm uninstall todo-chatbot

# Delete Dapr components
kubectl delete -f dapr/components/

# Stop Minikube
minikube stop

# Delete Minikube cluster (optional)
minikube delete
```

---

## Next Steps

- Implement reminder generation scheduler (Phase V - Part C)
- Add email/SMS notification delivery
- Set up monitoring with Prometheus and Grafana
- Configure CI/CD pipeline for automated deployments
- Add distributed tracing with Jaeger
- Implement dead letter queue monitoring

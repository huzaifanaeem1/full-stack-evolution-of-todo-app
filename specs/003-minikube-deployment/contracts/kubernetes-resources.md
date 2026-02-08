# Kubernetes Resource Templates: Todo Chatbot Deployment

**Feature**: 003-minikube-deployment
**Date**: 2026-02-08
**Purpose**: Define the structure and specifications for all Kubernetes resource templates

## Overview

This document describes the Kubernetes resource templates that will be created in the Helm chart. Each template generates one or more Kubernetes resources based on values from `values.yaml`.

## Template Files Structure

```
helm/todo-chatbot/templates/
├── _helpers.tpl              # Helper functions and template definitions
├── frontend-deployment.yaml  # Frontend Deployment resource
├── frontend-service.yaml     # Frontend Service resource
├── backend-deployment.yaml   # Backend Deployment resource
├── backend-service.yaml      # Backend Service resource
├── configmap.yaml           # ConfigMap resource
└── secrets.yaml             # Secrets resource
```

---

## Helper Templates (_helpers.tpl)

**Purpose**: Define reusable template functions for consistent labeling and naming

### Chart Name Helper

```yaml
{{- define "todo-chatbot.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}
```

### Full Name Helper

```yaml
{{- define "todo-chatbot.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
```

### Common Labels

```yaml
{{- define "todo-chatbot.labels" -}}
helm.sh/chart: {{ include "todo-chatbot.chart" . }}
{{ include "todo-chatbot.selectorLabels" . }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}
```

### Selector Labels

```yaml
{{- define "todo-chatbot.selectorLabels" -}}
app.kubernetes.io/name: {{ include "todo-chatbot.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

---

## Frontend Deployment Template

**File**: `frontend-deployment.yaml`

**Resource Type**: Deployment (apps/v1)

**Template Structure**:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "todo-chatbot.fullname" . }}-frontend
  namespace: {{ .Values.global.namespace }}
  labels:
    {{- include "todo-chatbot.labels" . | nindent 4 }}
    component: frontend
spec:
  replicas: {{ .Values.frontend.replicas }}
  selector:
    matchLabels:
      {{- include "todo-chatbot.selectorLabels" . | nindent 6 }}
      component: frontend
  template:
    metadata:
      labels:
        {{- include "todo-chatbot.selectorLabels" . | nindent 8 }}
        component: frontend
    spec:
      containers:
      - name: frontend
        image: "{{ .Values.frontend.image.repository }}:{{ .Values.frontend.image.tag }}"
        imagePullPolicy: {{ .Values.frontend.image.pullPolicy }}
        ports:
        - name: http
          containerPort: {{ .Values.frontend.service.targetPort }}
          protocol: TCP
        env:
        - name: NEXT_PUBLIC_API_BASE_URL
          value: "http://{{ include "todo-chatbot.fullname" . }}-backend:{{ .Values.backend.service.port }}"
        - name: ENVIRONMENT
          value: {{ .Values.frontend.env.ENVIRONMENT | quote }}
        livenessProbe:
          {{- toYaml .Values.frontend.livenessProbe | nindent 10 }}
        readinessProbe:
          {{- toYaml .Values.frontend.readinessProbe | nindent 10 }}
        resources:
          {{- toYaml .Values.frontend.resources | nindent 10 }}
```

**Key Features**:
- Uses Helm template functions for consistent naming
- Injects backend service URL automatically
- Configurable replicas, image, and resources
- Health checks from values.yaml

---

## Frontend Service Template

**File**: `frontend-service.yaml`

**Resource Type**: Service (v1)

**Template Structure**:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ include "todo-chatbot.fullname" . }}-frontend
  namespace: {{ .Values.global.namespace }}
  labels:
    {{- include "todo-chatbot.labels" . | nindent 4 }}
    component: frontend
spec:
  type: {{ .Values.frontend.service.type }}
  ports:
  - port: {{ .Values.frontend.service.port }}
    targetPort: {{ .Values.frontend.service.targetPort }}
    protocol: TCP
    name: http
    {{- if and (eq .Values.frontend.service.type "NodePort") .Values.frontend.service.nodePort }}
    nodePort: {{ .Values.frontend.service.nodePort }}
    {{- end }}
  selector:
    {{- include "todo-chatbot.selectorLabels" . | nindent 4 }}
    component: frontend
```

**Key Features**:
- NodePort type for external access
- Optional nodePort specification
- Selects frontend pods via labels

---

## Backend Deployment Template

**File**: `backend-deployment.yaml`

**Resource Type**: Deployment (apps/v1)

**Template Structure**:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "todo-chatbot.fullname" . }}-backend
  namespace: {{ .Values.global.namespace }}
  labels:
    {{- include "todo-chatbot.labels" . | nindent 4 }}
    component: backend
spec:
  replicas: {{ .Values.backend.replicas }}
  selector:
    matchLabels:
      {{- include "todo-chatbot.selectorLabels" . | nindent 6 }}
      component: backend
  template:
    metadata:
      labels:
        {{- include "todo-chatbot.selectorLabels" . | nindent 8 }}
        component: backend
    spec:
      containers:
      - name: backend
        image: "{{ .Values.backend.image.repository }}:{{ .Values.backend.image.tag }}"
        imagePullPolicy: {{ .Values.backend.image.pullPolicy }}
        ports:
        - name: http
          containerPort: {{ .Values.backend.service.targetPort }}
          protocol: TCP
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: {{ include "todo-chatbot.fullname" . }}-secrets
              key: databaseUrl
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: {{ include "todo-chatbot.fullname" . }}-secrets
              key: jwtSecret
        - name: ENVIRONMENT
          value: {{ .Values.backend.env.ENVIRONMENT | quote }}
        livenessProbe:
          {{- toYaml .Values.backend.livenessProbe | nindent 10 }}
        readinessProbe:
          {{- toYaml .Values.backend.readinessProbe | nindent 10 }}
        resources:
          {{- toYaml .Values.backend.resources | nindent 10 }}
```

**Key Features**:
- Injects secrets as environment variables
- Configurable replicas, image, and resources
- Health checks from values.yaml
- References Secrets resource for sensitive data

---

## Backend Service Template

**File**: `backend-service.yaml`

**Resource Type**: Service (v1)

**Template Structure**:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ include "todo-chatbot.fullname" . }}-backend
  namespace: {{ .Values.global.namespace }}
  labels:
    {{- include "todo-chatbot.labels" . | nindent 4 }}
    component: backend
spec:
  type: {{ .Values.backend.service.type }}
  ports:
  - port: {{ .Values.backend.service.port }}
    targetPort: {{ .Values.backend.service.targetPort }}
    protocol: TCP
    name: http
  selector:
    {{- include "todo-chatbot.selectorLabels" . | nindent 4 }}
    component: backend
```

**Key Features**:
- ClusterIP type for internal-only access
- Selects backend pods via labels
- Provides DNS name for service discovery

---

## ConfigMap Template

**File**: `configmap.yaml`

**Resource Type**: ConfigMap (v1)

**Template Structure**:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "todo-chatbot.fullname" . }}-config
  namespace: {{ .Values.global.namespace }}
  labels:
    {{- include "todo-chatbot.labels" . | nindent 4 }}
data:
  {{- range $key, $value := .Values.configMap.data }}
  {{ $key }}: {{ $value | quote }}
  {{- end }}
```

**Key Features**:
- Stores non-sensitive configuration
- Dynamic key-value pairs from values.yaml
- Can be mounted as environment variables or volumes

---

## Secrets Template

**File**: `secrets.yaml`

**Resource Type**: Secret (v1)

**Template Structure**:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: {{ include "todo-chatbot.fullname" . }}-secrets
  namespace: {{ .Values.global.namespace }}
  labels:
    {{- include "todo-chatbot.labels" . | nindent 4 }}
type: Opaque
data:
  databaseUrl: {{ .Values.secrets.databaseUrl | quote }}
  jwtSecret: {{ .Values.secrets.jwtSecret | quote }}
```

**Key Features**:
- Stores sensitive data (DATABASE_URL, JWT_SECRET)
- Values must be base64 encoded in values.yaml
- Referenced by backend deployment

---

## Resource Naming Convention

All resources follow a consistent naming pattern:

**Pattern**: `<release-name>-<chart-name>-<component>`

**Examples**:
- Deployment: `todo-chatbot-todo-chatbot-frontend`
- Service: `todo-chatbot-todo-chatbot-backend`
- ConfigMap: `todo-chatbot-todo-chatbot-config`
- Secrets: `todo-chatbot-todo-chatbot-secrets`

**Simplified** (when release name matches chart name):
- Deployment: `todo-chatbot-frontend`
- Service: `todo-chatbot-backend`

---

## Label Strategy

**Standard Labels** (applied to all resources):
- `helm.sh/chart`: Chart name and version
- `app.kubernetes.io/name`: Application name
- `app.kubernetes.io/instance`: Release name
- `app.kubernetes.io/version`: Application version
- `app.kubernetes.io/managed-by`: Helm

**Component Labels** (for service-specific resources):
- `component: frontend` - Frontend resources
- `component: backend` - Backend resources

**Selector Labels** (for pod selection):
- `app.kubernetes.io/name`: Application name
- `app.kubernetes.io/instance`: Release name
- `component`: Service component (frontend/backend)

---

## Template Validation

**Helm Template Rendering**:
```bash
# Render templates without installing
helm template todo-chatbot ./helm/todo-chatbot

# Render with custom values
helm template todo-chatbot ./helm/todo-chatbot -f custom-values.yaml

# Validate rendered templates
helm template todo-chatbot ./helm/todo-chatbot | kubectl apply --dry-run=client -f -
```

**Helm Lint**:
```bash
# Validate chart structure and templates
helm lint ./helm/todo-chatbot
```

**Kubernetes Validation**:
```bash
# Apply with dry-run to validate
kubectl apply --dry-run=server -f <rendered-template>.yaml
```

---

## Template Best Practices

1. **Use Helper Functions**: Consistent naming and labeling via `_helpers.tpl`
2. **Parameterize Everything**: All configuration via `values.yaml`
3. **Provide Defaults**: Sensible defaults for all values
4. **Validate Inputs**: Use Helm's `required` function for mandatory values
5. **Document Templates**: Comments explaining complex logic
6. **Test Thoroughly**: Render and validate before deployment
7. **Version Resources**: Include version labels for tracking
8. **Follow Conventions**: Kubernetes and Helm naming conventions

---

## Deployment Workflow

1. **Render Templates**: `helm template` to preview resources
2. **Validate Syntax**: `helm lint` to check chart structure
3. **Dry Run**: `helm install --dry-run` to validate against cluster
4. **Install**: `helm install` to deploy resources
5. **Verify**: `kubectl get all` to check resource creation
6. **Test**: Access application and verify functionality
7. **Upgrade**: `helm upgrade` to update deployment
8. **Rollback**: `helm rollback` if issues occur
9. **Uninstall**: `helm uninstall` to remove all resources

---

## Troubleshooting Templates

**Template Rendering Errors**:
```bash
# Debug template rendering
helm template todo-chatbot ./helm/todo-chatbot --debug
```

**Missing Values**:
```bash
# Check which values are used
helm template todo-chatbot ./helm/todo-chatbot --debug 2>&1 | grep "Values"
```

**Resource Creation Failures**:
```bash
# Check Helm release status
helm status todo-chatbot

# Check Kubernetes events
kubectl get events --sort-by='.lastTimestamp'
```

**Pod Startup Issues**:
```bash
# Check pod logs
kubectl logs <pod-name>

# Describe pod for events
kubectl describe pod <pod-name>
```

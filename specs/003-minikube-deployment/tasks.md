# Implementation Tasks: Local Kubernetes Deployment

**Feature**: 003-minikube-deployment
**Branch**: 003-minikube-deployment
**Spec**: [spec.md](./spec.md)
**Plan**: [plan.md](./plan.md)

## Task Summary

**Total Tasks**: 35
**User Stories**: 3 (P1, P2, P3)
**Parallel Opportunities**: 18 tasks marked [P]
**MVP Scope**: User Story 1 (Initial Service Deployment)

## Implementation Strategy

This deployment follows a strict spec-driven approach with no code modifications to Phase III application. Tasks are organized by user story to enable independent implementation and testing. Each user story delivers a complete, testable increment.

**Delivery Order**:
1. **MVP (US1)**: Initial deployment capability - Docker images, Helm chart, basic deployment
2. **US2**: Service communication validation and end-to-end testing
3. **US3**: Lifecycle management - clean install/uninstall workflows

## Task Dependencies

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational - Docker & Helm Structure)
    ↓
Phase 3 (US1 - Initial Deployment) ← MVP
    ↓
Phase 4 (US2 - Service Communication)
    ↓
Phase 5 (US3 - Lifecycle Management)
    ↓
Phase 6 (Polish & Documentation)
```

**Independent Stories**: US2 and US3 can be developed in parallel after US1 completes.

---

## Phase 1: Setup & Prerequisites

**Goal**: Initialize deployment infrastructure and verify prerequisites

**Tasks**:

- [x] T001 Create deployment directory structure (docker/, helm/)
- [x] T002 Create .dockerignore for frontend in docker/frontend/.dockerignore
- [x] T003 Create .dockerignore for backend in docker/backend/.dockerignore
- [x] T004 Verify Minikube installation and start cluster
- [x] T005 Verify Docker, kubectl, and Helm installations
- [ ] T006 Document AI DevOps tools setup (Gordon, kubectl-ai, kagent) in docs/ai-devops-setup.md

**Acceptance**: Directory structure exists, prerequisites verified, Minikube cluster running

---

## Phase 2: Foundational - Docker Images & Helm Structure

**Goal**: Create Docker images and Helm chart structure (blocking prerequisites for all user stories)

### Docker Image Tasks

- [x] T007 [P] Create frontend Dockerfile with multi-stage build in docker/frontend/Dockerfile
- [x] T008 [P] Create backend Dockerfile with multi-stage build in docker/backend/Dockerfile
- [x] T009 [P] Build frontend Docker image (todo-frontend:v1.0.0)
- [x] T010 [P] Build backend Docker image (todo-backend:v1.0.0)
- [x] T011 Load frontend image into Minikube
- [x] T012 Load backend image into Minikube
- [x] T013 Verify images available in Minikube registry

### Helm Chart Structure Tasks

- [x] T014 Create Helm chart directory structure in helm/todo-chatbot/
- [x] T015 Create Chart.yaml with metadata in helm/todo-chatbot/Chart.yaml
- [x] T016 Create values.yaml with default configuration in helm/todo-chatbot/values.yaml
- [x] T017 Create _helpers.tpl with template functions in helm/todo-chatbot/templates/_helpers.tpl

**Acceptance**: Docker images built and loaded, Helm chart structure created

---

## Phase 3: User Story 1 - Initial Service Deployment (P1)

**Story Goal**: Deploy Todo Chatbot to Minikube with Helm, all pods Running

**Independent Test**: Start clean Minikube, run `helm install`, verify all pods reach Running state within 5 minutes

### Kubernetes Resource Templates

- [x] T018 [P] [US1] Create frontend Deployment template in helm/todo-chatbot/templates/frontend-deployment.yaml
- [x] T019 [P] [US1] Create backend Deployment template in helm/todo-chatbot/templates/backend-deployment.yaml
- [x] T020 [P] [US1] Create frontend Service template in helm/todo-chatbot/templates/frontend-service.yaml
- [x] T021 [P] [US1] Create backend Service template in helm/todo-chatbot/templates/backend-service.yaml
- [x] T022 [P] [US1] Create ConfigMap template in helm/todo-chatbot/templates/configmap.yaml
- [x] T023 [P] [US1] Create Secrets template in helm/todo-chatbot/templates/secrets.yaml

### Deployment Tasks

- [x] T024 [US1] Render Helm templates and validate syntax with `helm template`
- [x] T025 [US1] Lint Helm chart with `helm lint`
- [x] T026 [US1] Prepare base64-encoded secrets for DATABASE_URL and JWT_SECRET
- [x] T027 [US1] Install Helm chart with `helm install todo-chatbot`
- [x] T028 [US1] Wait for pods to reach Running state (kubectl wait)
- [x] T029 [US1] Verify all Kubernetes resources created (Deployments, Services, ConfigMaps, Secrets)

**Story Acceptance**:
- ✅ Helm install completes successfully
- ✅ All pods reach Running state within 5 minutes
- ✅ Each service has its own Docker image and Deployment
- ✅ No pod restarts or crash loops

---

## Phase 4: User Story 2 - Service Communication and Accessibility (P2)

**Story Goal**: Verify services communicate and application is accessible

**Independent Test**: Access frontend URL, verify UI loads, confirm frontend-to-backend API calls succeed

### Service Validation Tasks

- [x] T030 [US2] Get frontend service URL with `minikube service todo-chatbot-frontend --url`
- [x] T031 [US2] Verify frontend accessible in browser
- [x] T032 [US2] Test backend health endpoint with port-forward
- [x] T033 [US2] Verify frontend can reach backend via Kubernetes DNS
- [ ] T034 [US2] Test end-to-end application functionality (login, create task, view tasks)

**Story Acceptance**:
- ✅ Frontend loads successfully in browser
- ✅ Backend responds to health checks
- ✅ Frontend-to-backend API calls succeed (100% success rate)
- ✅ All Phase III features work correctly (auth, tasks, chatbot)

---

## Phase 5: User Story 3 - Deployment Lifecycle Management (P3)

**Story Goal**: Support clean install/uninstall and reinstall workflows

**Independent Test**: Helm install, verify deployment, Helm uninstall, confirm no residual resources, reinstall successfully

### Lifecycle Management Tasks

- [ ] T035 [US3] Test Helm uninstall with `helm uninstall todo-chatbot`
- [ ] T036 [US3] Verify all resources removed (kubectl get all)
- [ ] T037 [US3] Verify no residual ConfigMaps or Secrets
- [ ] T038 [US3] Test reinstallation after uninstall
- [ ] T039 [US3] Verify reinstall identical to initial install
- [ ] T040 [US3] Test Helm upgrade workflow with new image tags
- [ ] T041 [US3] Test Helm rollback to previous revision

**Story Acceptance**:
- ✅ Helm uninstall removes 100% of resources within 2 minutes
- ✅ No residual resources remain after uninstall
- ✅ Reinstallation succeeds identically to initial install
- ✅ Upgrade and rollback workflows function correctly

---

## Phase 6: Polish & Cross-Cutting Concerns

**Goal**: Documentation, optimization, and final validation

### Documentation Tasks

- [ ] T042 [P] Create Helm chart README in helm/todo-chatbot/README.md
- [ ] T043 [P] Document deployment runbook in docs/deployment-runbook.md
- [ ] T044 [P] Document troubleshooting guide in docs/troubleshooting.md
- [ ] T045 [P] Update main README with Phase IV deployment instructions

### Validation Tasks

- [ ] T046 Test deployment on fresh Minikube cluster (clean slate validation)
- [ ] T047 Verify all success criteria from spec.md
- [ ] T048 Validate AI DevOps tool integration (if tools available)
- [ ] T049 Performance validation (pods Running < 5 min, frontend accessible < 1 min)
- [ ] T050 Security validation (secrets not in plain text, no hardcoded values)

**Acceptance**: All documentation complete, all success criteria met, deployment repeatable

---

## Parallel Execution Opportunities

### Phase 2 Parallelization
```bash
# Docker images can be built in parallel
docker build -t todo-frontend:v1.0.0 -f docker/frontend/Dockerfile ./frontend &
docker build -t todo-backend:v1.0.0 -f docker/backend/Dockerfile ./backend &
wait

# Helm templates can be created in parallel
# T018-T023: All template files are independent
```

### Phase 3 Parallelization
```bash
# All Kubernetes resource templates (T018-T023) can be created in parallel
# They are independent files with no dependencies on each other
```

### Phase 6 Parallelization
```bash
# All documentation tasks (T042-T045) can be done in parallel
# They are independent files
```

---

## AI DevOps Tool Integration Points

### Gordon (Docker AI)
- **T007**: Generate frontend Dockerfile
  - Prompt: "Create production-ready multi-stage Dockerfile for Next.js 16 application with App Router, Node 18 Alpine base"
- **T008**: Generate backend Dockerfile
  - Prompt: "Create production-ready multi-stage Dockerfile for FastAPI application, Python 3.11 slim base"

### kubectl-ai
- **T018-T023**: Generate Kubernetes resource manifests
  - Prompt: "Create Kubernetes Deployment for Next.js frontend with health checks, resource limits, environment variables"
- **T032-T033**: Debug deployment issues
  - Prompt: "Why is my pod in CrashLoopBackOff state?"

### kagent
- **T049**: Analyze cluster performance
  - Prompt: "Analyze resource usage for todo-chatbot deployment and identify bottlenecks"

**Fallback**: Manual creation using documented best practices if AI tools unavailable

---

## Task Execution Guidelines

### Prerequisites for Each Phase
- **Phase 1**: None (starting point)
- **Phase 2**: Phase 1 complete
- **Phase 3**: Phase 2 complete (Docker images and Helm structure ready)
- **Phase 4**: Phase 3 complete (deployment successful)
- **Phase 5**: Phase 3 complete (can run in parallel with Phase 4)
- **Phase 6**: Phases 3, 4, 5 complete

### Task Format Legend
- `[ ]`: Task checkbox (mark with `[x]` when complete)
- `T###`: Sequential task ID
- `[P]`: Parallelizable task (can run concurrently with other [P] tasks)
- `[US#]`: User story label (maps to spec.md user stories)

### Validation Checkpoints
- After Phase 2: Docker images built and loaded into Minikube
- After Phase 3: Helm install successful, all pods Running
- After Phase 4: Application accessible and functional
- After Phase 5: Clean install/uninstall workflows validated
- After Phase 6: All documentation complete, ready for production use

---

## Success Criteria Mapping

From spec.md, mapped to tasks:

- **SC-001**: Helm installation < 5 minutes → T027, T028
- **SC-002**: Pods Running < 5 minutes → T028
- **SC-003**: Frontend accessible < 1 minute → T030, T031
- **SC-004**: Backend health check < 30 seconds → T032
- **SC-005**: 100% API success rate → T033, T034
- **SC-006**: 0 pod restarts in 30 minutes → T029, T049
- **SC-007**: Helm uninstall < 2 minutes → T035, T036
- **SC-008**: Reinstall identical to initial → T038, T039
- **SC-009**: Phase III features work → T034
- **SC-010**: Repeatable deployment → T046, T047

---

## Risk Mitigation Tasks

**Risk**: Docker images too large
- **Mitigation**: T007, T008 use multi-stage builds and Alpine/slim base images

**Risk**: Pods fail to start
- **Mitigation**: T024, T025 validate templates before deployment

**Risk**: Service communication fails
- **Mitigation**: T033 validates Kubernetes DNS and service discovery

**Risk**: AI tools unavailable
- **Mitigation**: All tasks have manual fallback documented in plan.md

**Risk**: Phase III functionality breaks
- **Mitigation**: T034 validates end-to-end application functionality

---

## Notes

- **No Code Modifications**: Phase III application code remains unchanged
- **AI Tools Optional**: All tasks can be completed manually if AI tools unavailable
- **Incremental Delivery**: Each user story delivers a complete, testable increment
- **Independent Testing**: Each user story has clear independent test criteria
- **Rollback Strategy**: Helm provides built-in rollback capability (T041)

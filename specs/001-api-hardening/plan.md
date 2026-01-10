# Implementation Plan: API Hardening and Validation

**Branch**: `001-api-hardening` | **Date**: 2026-01-09 | **Spec**: [link](./spec.md)
**Input**: Feature specification from `/specs/001-api-hardening/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implementation of security hardening and validation for the Todo Web Application API. This phase focuses on ensuring all API endpoints properly enforce JWT authentication, validate user ownership of data, and return appropriate HTTP status codes. The implementation will strengthen the authentication and authorization layers to prevent cross-user data access while maintaining proper error handling and API behavior as specified in the requirements.

## Technical Context

**Language/Version**: Python 3.11, JavaScript/TypeScript (Next.js 16+)
**Primary Dependencies**: FastAPI, Next.js with App Router, SQLModel, Neon PostgreSQL driver, Better Auth
**Storage**: Neon Serverless PostgreSQL database with SQLModel ORM
**Testing**: pytest for backend, Jest/React Testing Library for frontend
**Target Platform**: Web application (Linux/Mac/Windows server with browser clients)
**Project Type**: Full-stack web application with separate frontend and backend services
**Performance Goals**: <200ms p95 API response time, sub-second UI interactions
**Constraints**: JWT-based authentication, user data isolation, secure API communication
**Scale/Scope**: Multi-user todo application with secure authentication and task management

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Spec-Driven Development Compliance
- [x] Specification document exists and is complete in `/specs/001-api-hardening/spec.md`
- [x] Plan document created based on spec requirements
- [x] Tasks will be generated from plan before implementation begins

### Technology Stack Verification
- [x] Frontend uses Next.js 16+ with App Router
- [x] Backend uses FastAPI framework
- [x] SQLModel ORM is used for database operations
- [x] Neon Serverless PostgreSQL is the database
- [x] Better Auth is used for JWT-based authentication
- [x] REST API design is followed (no GraphQL/other protocols)

### Security Requirements Check
- [x] All API endpoints require JWT token verification
- [x] User ID is extracted from JWT payload for data isolation
- [x] Users only access their own data/tasks
- [x] JWT secret is shared via environment variables only
- [x] No hardcoded secrets in source code

### Architecture Requirements
- [x] Backend and frontend are separate deployable services
- [x] Authentication is mandatory for all features
- [x] Data access is user-isolated
- [x] Phase I (CLI) and Phase II (Web App) remain separate

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── user.py
│   │   └── task.py
│   ├── services/
│   │   ├── auth_service.py
│   │   └── task_service.py
│   ├── api/
│   │   ├── auth_routes.py
│   │   └── task_routes.py
│   └── config/
│       └── database.py
├── requirements.txt
├── alembic/
└── .env.example

frontend/
├── src/
│   ├── app/
│   │   ├── login/
│   │   ├── register/
│   │   ├── dashboard/
│   │   └── layout.tsx
│   ├── components/
│   │   ├── TaskList.tsx
│   │   ├── TaskItem.tsx
│   │   └── ProtectedRoute.tsx
│   ├── services/
│   │   ├── auth.ts
│   │   └── api.ts
│   ├── types/
│   │   └── index.ts
│   └── utils/
├── package.json
├── .env.local.example
└── tailwind.config.ts

specs/001-api-hardening/
├── spec.md
├── plan.md
└── tasks.md

tests/
├── backend/
│   ├── unit/
│   └── integration/
└── frontend/
    ├── unit/
    └── integration/
```

**Structure Decision**: Web application with separate frontend (Next.js) and backend (FastAPI) services following the existing architecture established in Phase II - Part 2. The API hardening and validation work will primarily focus on enhancing security in both backend API endpoints and frontend API consumption patterns.

## Implementation Approach

### Backend Validation
- Verify all API endpoints enforce JWT token verification using middleware
- Validate user_id in URL path matches authenticated user's ID from JWT payload
- Ensure consistent error responses (401 for unauthorized, 403 for forbidden access)
- Test cross-user access attempts to prevent data leakage
- Verify proper HTTP status codes (200/201/401/403/404) for all endpoints

### Frontend Validation
- Confirm JWT tokens are attached to all API calls automatically
- Implement proper handling of 401/403 responses (redirect to login, show error messages)
- Prevent UI from displaying unauthorized data or allowing unauthorized actions
- Verify that all API calls use the authenticated user's ID in the URL path
- Test error handling for invalid/expired tokens

### Configuration Plan
- Verify .env.example includes all required environment variables
- Ensure DATABASE_URL is not hardcoded in source code
- Validate JWT secret is properly configured via environment variables
- Confirm proper configuration for both development and production environments

### Documentation Plan
- Update README with project overview and technology stack
- Add run instructions for both backend and frontend
- Document authentication flow and security measures
- Include API endpoint documentation with expected responses
- Add testing scenarios for security validation

### Testing Plan
- Manual test scenarios for unauthorized access attempts
- Cross-user access prevention validation
- CRUD operations testing with proper authentication
- Error response validation for different failure scenarios
- Token expiration and refresh testing

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |

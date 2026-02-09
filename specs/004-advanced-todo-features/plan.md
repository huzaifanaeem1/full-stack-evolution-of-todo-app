# Implementation Plan: Advanced and Intermediate Todo Features

**Branch**: `004-advanced-todo-features` | **Date**: 2026-02-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-advanced-todo-features/spec.md`

## Summary

This plan extends the existing todo application with advanced organizational and automation features including task priorities (high/medium/low), tags for categorization, due dates for deadline tracking, search/filter/sort capabilities for task discovery, and recurring tasks (daily/weekly/monthly) for automation. All features maintain backward compatibility with Phase I-IV functionality and follow strict user isolation requirements.

**Technical Approach**: Extend existing Task model with new optional fields, create Tag entity with many-to-many relationship, implement query parameter-based filtering/sorting in existing REST endpoints, and add synchronous recurring task generation logic triggered by API calls.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.0+ (frontend)
**Primary Dependencies**: FastAPI, SQLModel, Neon PostgreSQL driver, Better Auth, Next.js 16+ App Router
**Storage**: Neon Serverless PostgreSQL with SQLModel ORM
**Testing**: pytest (backend), Jest/React Testing Library (frontend)
**Target Platform**: Web application (backend: Linux server, frontend: browser)
**Project Type**: Web application (separate backend and frontend services)
**Performance Goals**: <1s for search/filter/sort operations on 1000 tasks, <200ms for CRUD operations
**Constraints**: No infrastructure changes, backward compatible with existing Phase I-IV functionality, user data isolation mandatory
**Scale/Scope**: Support 10k+ users, 1000+ tasks per user, 20+ tags per user

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Spec-Driven Development Compliance
- [x] Specification document exists and is complete in `/specs/004-advanced-todo-features/spec.md`
- [x] Plan document will be created based on spec requirements
- [x] Tasks will be generated from plan before implementation begins

### Technology Stack Verification
- [x] Frontend will use Next.js 16+ with App Router
- [x] Backend will use FastAPI framework
- [x] SQLModel ORM will be used for database operations
- [x] Neon Serverless PostgreSQL will be the database
- [x] Better Auth will be used for JWT-based authentication
- [x] REST API design will be followed (no GraphQL/other protocols)

### Security Requirements Check
- [x] All API endpoints will require JWT token verification
- [x] User ID will be extracted from JWT payload for data isolation
- [x] Users will only access their own data/tasks
- [x] JWT secret will be shared via environment variables only
- [x] No hardcoded secrets in source code

### Architecture Requirements
- [x] Backend and frontend will be separate deployable services
- [x] Authentication will be mandatory for all features
- [x] Data access will be user-isolated
- [x] Phase I (CLI) and Phase II (Web App) remain separate

### Phase V - Part A Specific Requirements
- [x] No infrastructure changes (Kubernetes, Docker, Helm unchanged)
- [x] No Kafka, Dapr, or cloud deployment logic
- [x] Backward compatibility with existing Phase I-IV functionality maintained
- [x] All features exposed through REST API endpoints
- [x] All features accessible via AI chatbot interface

## Project Structure

### Documentation (this feature)

```text
specs/004-advanced-todo-features/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (technical decisions)
├── data-model.md        # Phase 1 output (entity definitions)
├── quickstart.md        # Phase 1 output (implementation guide)
├── contracts/           # Phase 1 output (API contracts)
│   ├── tasks-extended.openapi.yaml
│   └── schemas.yaml
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── task.py          # EXTEND: Add priority, due_date, recurrence fields
│   │   ├── tag.py           # NEW: Tag entity
│   │   └── task_tag.py      # NEW: Many-to-many association table
│   ├── services/
│   │   ├── task_service.py  # EXTEND: Add search, filter, sort, recurring logic
│   │   └── tag_service.py   # NEW: Tag management operations
│   ├── api/
│   │   ├── tasks.py         # EXTEND: Add query params for search/filter/sort
│   │   └── tags.py          # NEW: Tag endpoints (optional, for tag management)
│   └── config/
│       └── database.py      # EXTEND: Add migration for new fields/tables
└── tests/
    ├── integration/
    │   ├── test_task_priority.py
    │   ├── test_task_tags.py
    │   ├── test_task_search.py
    │   └── test_recurring_tasks.py
    └── unit/
        ├── test_task_model.py
        └── test_tag_model.py

frontend/
├── src/
│   ├── components/
│   │   ├── TaskList.tsx     # EXTEND: Display priority, tags, due dates
│   │   ├── TaskForm.tsx     # EXTEND: Add priority, tags, due date inputs
│   │   └── TaskFilters.tsx  # NEW: Search, filter, sort controls
│   ├── app/
│   │   └── tasks/
│   │       └── page.tsx     # EXTEND: Integrate new features
│   └── lib/
│       └── api.ts           # EXTEND: Add new API calls
└── tests/
    └── components/
        ├── TaskList.test.tsx
        └── TaskFilters.test.tsx
```

**Structure Decision**: Using existing web application structure (Option 2) with separate backend and frontend services. Extensions will be made to existing files where possible to maintain backward compatibility. New entities (Tag, TaskTag) will be added as separate modules.

## Complexity Tracking

> No constitution violations - all requirements align with existing architecture and constraints.

## Phase 0: Research & Technical Decisions

**Status**: Complete (see [research.md](./research.md))

**Key Decisions**:
1. **Priority Storage**: Enum field in Task model (high/medium/low) with database-level constraint
2. **Tag Implementation**: Separate Tag table with many-to-many relationship via TaskTag association table
3. **Search Strategy**: PostgreSQL ILIKE for case-insensitive substring matching on title and description
4. **Filter/Sort Implementation**: SQLModel query builder with dynamic WHERE clauses and ORDER BY
5. **Recurring Task Logic**: Synchronous generation on task completion or explicit trigger endpoint
6. **Date Storage**: PostgreSQL DATE type for due_date field (no time component)

## Phase 1: Design & Contracts

**Status**: Complete (see [data-model.md](./data-model.md) and [contracts/](./contracts/))

### Data Model Summary

**Extended Task Entity**:
- Add `priority` field (enum: high, medium, low, default: medium)
- Add `due_date` field (optional DATE)
- Add `is_recurring` field (boolean, default: false)
- Add `recurrence_frequency` field (optional enum: daily, weekly, monthly)
- Add `last_recurrence_date` field (optional DATE, tracks last generated instance)
- Maintain all existing fields for backward compatibility

**New Tag Entity**:
- `id` (UUID, primary key)
- `name` (string, unique per user)
- `user_id` (UUID, foreign key to User)
- `created_at` (timestamp)

**New TaskTag Association**:
- `task_id` (UUID, foreign key to Task)
- `tag_id` (UUID, foreign key to Tag)
- Composite primary key (task_id, tag_id)

### API Contract Summary

**Extended GET /{user_id}/tasks**:
- Add query parameters: `search`, `status`, `priority`, `tags`, `sort_by`, `sort_order`
- Response includes new fields: priority, due_date, tags[], is_recurring, recurrence_frequency

**Extended POST /{user_id}/tasks**:
- Request body includes optional: priority, due_date, tags[], is_recurring, recurrence_frequency
- Validation: priority enum, due_date format, tag name constraints

**Extended PUT /{user_id}/tasks/{id}**:
- Request body includes optional: priority, due_date, tags[], is_recurring, recurrence_frequency
- Supports partial updates

**New POST /{user_id}/tasks/{id}/generate-recurrence**:
- Manually trigger recurring task instance generation
- Returns newly created task instance

**New GET /{user_id}/tags**:
- List all tags for user
- Response: array of tag objects with usage count

## Phase 2: Implementation Readiness

**Prerequisites for /sp.tasks**:
- [x] research.md complete with all technical decisions documented
- [x] data-model.md complete with entity definitions and relationships
- [x] contracts/ directory complete with OpenAPI specifications
- [x] quickstart.md complete with implementation guidance
- [x] Constitution check passed (no violations)

**Next Command**: `/sp.tasks` to generate implementation task list

## Risk Analysis

### Technical Risks

1. **Database Migration Complexity**
   - Risk: Adding new fields and tables to production database
   - Mitigation: Use Alembic migrations with rollback capability, test on staging first
   - Impact: Medium

2. **Query Performance with Filters**
   - Risk: Complex filter combinations may slow down queries on large datasets
   - Mitigation: Add database indexes on priority, due_date, and tag relationships
   - Impact: Low (within 1000 task constraint)

3. **Recurring Task Duplication**
   - Risk: Race conditions could create duplicate recurring instances
   - Mitigation: Use database-level unique constraints and transaction isolation
   - Impact: Medium

### Integration Risks

1. **Backward Compatibility**
   - Risk: Existing clients may break with new required fields
   - Mitigation: All new fields are optional, existing endpoints return same structure
   - Impact: Low

2. **AI Chatbot Integration**
   - Risk: Chatbot may not handle new task attributes correctly
   - Mitigation: Update chatbot intent mapping and response templates
   - Impact: Medium

## Architectural Decision Records

No ADRs required for this phase - all decisions follow existing patterns and constitution requirements.

## Notes

- All new fields are optional to maintain backward compatibility
- Recurring task generation is synchronous (no background jobs) per constitution constraints
- Tag filtering uses "any tag" logic (OR operation) as documented in spec assumptions
- Tasks without due dates sort to end of list when sorting by due_date
- Priority defaults to "medium" when not specified
- Search is case-insensitive substring matching (not full-text search)

---
id: 0002
title: Advanced Todo Features Implementation Plan
stage: plan
date: 2026-02-09
surface: agent
model: claude-sonnet-4-5
feature: 004-advanced-todo-features
branch: 004-advanced-todo-features
user: system
command: /sp.plan
labels: ["planning", "phase-v", "advanced-features", "priorities", "tags", "search", "filter", "sort", "due-dates", "recurring-tasks", "data-model", "api-contracts"]
links:
  spec: specs/004-advanced-todo-features/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/004-advanced-todo-features/plan.md
  - specs/004-advanced-todo-features/research.md
  - specs/004-advanced-todo-features/data-model.md
  - specs/004-advanced-todo-features/contracts/tasks-extended.openapi.yaml
  - specs/004-advanced-todo-features/quickstart.md
tests:
  - none
---

## Prompt

PHASE V – PART A
PLAN PROMPT

INSTRUCTIONS TO AGENT

You are in the PLAN phase.

DO NOT write code.
DO NOT create tasks.
DO NOT modify infrastructure.

OBJECTIVE

Create a technical plan describing how the specified features will be implemented.

PLAN MUST INCLUDE

Data model changes

API changes

Search, filter, sort logic

Recurring task behavior (synchronous)

MCP tool updates

Chatbot intent mapping

Validation and error handling

END OF PLAN PROMPT

WAIT INSTRUCTION:
STOP HERE.
WAIT FOR USER TO PROVIDE THE TASKS PROMPT.

## Response snapshot

Created comprehensive implementation plan for Phase V - Part A advanced todo features with complete Phase 0 (Research) and Phase 1 (Design & Contracts) deliverables.

**Plan Highlights**:
- Extended Task model with priority, due_date, is_recurring, recurrence_frequency, last_recurrence_date fields
- New Tag entity with many-to-many relationship via TaskTag association table
- Query parameter-based filtering and sorting in existing REST endpoints
- Synchronous recurring task generation (no background jobs per constitution)
- PostgreSQL ILIKE for case-insensitive search
- All new fields optional for backward compatibility

**Phase 0 - Research Completed**:
- Priority storage: Enum field with database constraint
- Tag implementation: Separate table with many-to-many relationship
- Search strategy: PostgreSQL ILIKE substring matching
- Filter/sort: SQLModel query builder with dynamic clauses
- Recurring logic: Synchronous generation on completion or manual trigger
- Date storage: PostgreSQL DATE type (no time component)
- Tag filtering: OR logic (matches any tag)

**Phase 1 - Design & Contracts Completed**:
- Data model with 3 entities: Task (extended), Tag (new), TaskTag (new)
- Database migration plan with up/down scripts
- OpenAPI specification for extended tasks API
- Request/response models with validation
- Quickstart implementation guide with 6 phases

**Technical Decisions**:
- No new dependencies required (existing stack sufficient)
- All features implementable with FastAPI + SQLModel + PostgreSQL
- Performance targets: <1s search/filter/sort, <200ms CRUD
- Indexes on priority, due_date, tags for query optimization
- User isolation enforced at all levels

**Constitution Compliance**:
- All checks passed (no violations)
- No infrastructure changes
- Backward compatible with Phase I-IV
- REST API only (no GraphQL)
- User data isolation maintained

## Outcome

- ✅ Impact: Complete implementation plan with research, data model, API contracts, and quickstart guide for Phase V - Part A
- 🧪 Tests: N/A (planning phase - no code written)
- 📁 Files: 5 files created (plan.md, research.md, data-model.md, contracts/tasks-extended.openapi.yaml, quickstart.md)
- 🔁 Next prompts: User should provide TASKS PROMPT (use /sp.tasks to generate implementation task list)
- 🧠 Reflection: Successfully created a comprehensive technical plan that extends existing architecture without breaking changes. All design decisions documented with rationale. Ready for task generation and implementation.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Constitution check PASS (all requirements met, no violations)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A

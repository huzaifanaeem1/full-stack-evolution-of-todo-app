# Tasks: Advanced and Intermediate Todo Features

**Input**: Design documents from `/specs/004-advanced-todo-features/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/
**Constitution Compliance**: All tasks must comply with constitution requirements

**Tests**: Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Paths shown below use web application structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure verification

- [X] T001 Verify project structure matches plan.md specifications
- [X] T002 [P] Verify Python 3.11+ and FastAPI dependencies are installed
- [X] T003 [P] Verify Next.js 16+ and TypeScript 5.0+ dependencies are installed
- [X] T004 [P] Verify database connection to Neon Serverless PostgreSQL

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Create Alembic migration for advanced todo features in backend/alembic/versions/
- [X] T006 [P] Create PriorityLevel enum in backend/src/models/task.py
- [X] T007 [P] Create RecurrenceFrequency enum in backend/src/models/task.py
- [X] T008 Add priority column to task table in migration (ENUM, default 'medium')
- [X] T009 Add due_date column to task table in migration (DATE, nullable)
- [X] T010 Add is_recurring column to task table in migration (BOOLEAN, default false)
- [X] T011 Add recurrence_frequency column to task table in migration (ENUM, nullable)
- [X] T012 Add last_recurrence_date column to task table in migration (DATE, nullable)
- [X] T013 Create tag table in migration with id, name, user_id, created_at
- [X] T014 Create task_tag association table in migration with task_id, tag_id
- [X] T015 Add indexes on task.priority, task.due_date in migration
- [X] T016 Add composite indexes on (user_id, priority) and (user_id, due_date) in migration
- [X] T017 Add unique constraint on (tag.user_id, LOWER(tag.name)) in migration
- [X] T018 Add check constraint for recurring task validation in migration
- [X] T019 Run migration and verify all tables/columns created successfully
- [X] T020 Test migration rollback to ensure it works correctly

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Task Priority Management (Priority: P1) 🎯 MVP

**Goal**: Enable users to assign and manage priority levels (high, medium, low) for tasks

**Independent Test**: Create tasks with different priorities, update priorities, verify persistence and retrieval

### Implementation for User Story 1

- [X] T021 [P] [US1] Extend TaskBase model with priority field in backend/src/models/task.py
- [X] T022 [P] [US1] Update TaskCreate schema to include optional priority field in backend/src/models/task.py
- [X] T023 [P] [US1] Update TaskRead schema to include priority field in backend/src/models/task.py
- [X] T024 [P] [US1] Update TaskUpdate schema to include optional priority field in backend/src/models/task.py
- [X] T025 [US1] Add priority validation in TaskCreate schema in backend/src/models/task.py
- [X] T026 [US1] Update create_task_for_user to handle priority in backend/src/services/task_service.py
- [X] T027 [US1] Update update_task_by_id_and_user to handle priority in backend/src/services/task_service.py
- [X] T028 [US1] Verify GET /{user_id}/tasks returns priority field in backend/src/api/tasks.py
- [X] T029 [US1] Verify POST /{user_id}/tasks accepts priority field in backend/src/api/tasks.py
- [X] T030 [US1] Verify PUT /{user_id}/tasks/{id} accepts priority field in backend/src/api/tasks.py
- [X] T031 [P] [US1] Add priority field to Task type definition in frontend/src/types/index.ts
- [X] T032 [US1] Add priority dropdown to TaskForm component in frontend/src/components/TaskForm.tsx
- [X] T033 [US1] Display priority badge in TaskList component in frontend/src/components/TaskItem.tsx
- [X] T034 [US1] Add priority color coding (red=high, yellow=medium, green=low) in frontend/src/components/TaskItem.tsx

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Due Date Management (Priority: P2)

**Goal**: Enable users to set and manage due dates for deadline tracking

**Independent Test**: Create tasks with due dates, update dates, remove dates, verify persistence

### Implementation for User Story 2

- [X] T035 [P] [US2] Extend TaskBase model with due_date field in backend/src/models/task.py
- [X] T036 [P] [US2] Update TaskCreate schema to include optional due_date field in backend/src/models/task.py
- [X] T037 [P] [US2] Update TaskRead schema to include due_date field in backend/src/models/task.py
- [X] T038 [P] [US2] Update TaskUpdate schema to include optional due_date field in backend/src/models/task.py
- [X] T039 [US2] Add due_date validation (ISO 8601 format) in TaskCreate schema in backend/src/models/task.py
- [X] T040 [US2] Update create_task_for_user to handle due_date in backend/src/services/task_service.py
- [X] T041 [US2] Update update_task_by_id_and_user to handle due_date in backend/src/services/task_service.py
- [X] T042 [US2] Verify GET /{user_id}/tasks returns due_date field in backend/src/api/tasks.py
- [X] T043 [US2] Verify POST /{user_id}/tasks accepts due_date field in backend/src/api/tasks.py
- [X] T044 [US2] Verify PUT /{user_id}/tasks/{id} accepts due_date field in backend/src/api/tasks.py
- [X] T045 [P] [US2] Add due_date field to Task type definition in frontend/src/types/index.ts
- [X] T046 [US2] Add date picker to TaskForm component in frontend/src/components/TaskForm.tsx
- [X] T047 [US2] Display due date in TaskList component in frontend/src/components/TaskItem.tsx
- [X] T048 [US2] Add overdue indicator for past due dates in frontend/src/components/TaskItem.tsx

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Tags and Categories (Priority: P3)

**Goal**: Enable users to organize tasks using tags for flexible categorization

**Independent Test**: Create tasks with tags, add/remove tags, verify tag persistence and reuse

### Implementation for User Story 3

- [X] T049 [P] [US3] Create Tag model in backend/src/models/tag.py
- [X] T050 [P] [US3] Create TaskTag association model in backend/src/models/task_tag.py
- [X] T051 [P] [US3] Create TagBase schema in backend/src/models/tag.py
- [X] T052 [P] [US3] Create TagRead schema in backend/src/models/tag.py
- [X] T053 [US3] Add tag name validation (alphanumeric, spaces, hyphens, underscores) in backend/src/models/tag.py
- [X] T054 [US3] Create tag_service.py with get_or_create_tag function in backend/src/services/tag_service.py
- [X] T055 [US3] Implement assign_tags_to_task function in backend/src/services/tag_service.py
- [X] T056 [US3] Implement get_tags_for_task function in backend/src/services/tag_service.py
- [X] T057 [US3] Implement get_tags_for_user function in backend/src/services/tag_service.py
- [X] T058 [US3] Update TaskCreate schema to include optional tags array in backend/src/models/task.py
- [X] T059 [US3] Update TaskRead schema to include tags array in backend/src/models/task.py
- [X] T060 [US3] Update TaskUpdate schema to include optional tags array in backend/src/models/task.py
- [X] T061 [US3] Extend create_task_for_user to handle tags in backend/src/services/task_service.py
- [X] T062 [US3] Extend update_task_by_id_and_user to handle tags in backend/src/services/task_service.py
- [X] T063 [US3] Extend get_tasks_for_user to populate tags in backend/src/services/task_service.py
- [X] T064 [US3] Update POST /{user_id}/tasks to accept tags in backend/src/api/tasks.py
- [X] T065 [US3] Update PUT /{user_id}/tasks/{id} to accept tags in backend/src/api/tasks.py
- [X] T066 [US3] Update GET /{user_id}/tasks to return tags in backend/src/api/tasks.py
- [X] T067 [US3] Add GET /{user_id}/tags endpoint in backend/src/api/tasks.py
- [X] T068 [P] [US3] Add tags field to Task type definition in frontend/src/types/index.ts
- [X] T069 [P] [US3] Add getTags API function in frontend/src/services/api.ts
- [X] T070 [US3] Add tag input component to TaskForm in frontend/src/components/TaskForm.tsx
- [X] T071 [US3] Display tags as chips in TaskList in frontend/src/components/TaskItem.tsx

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 4 - Search, Filter, and Sort (Priority: P4)

**Goal**: Enable users to search, filter, and sort tasks for efficient task discovery

**Independent Test**: Create diverse tasks, verify search results, filter behavior, and sort ordering

### Implementation for User Story 4

- [X] T072 [P] [US4] Implement search_tasks function with ILIKE in backend/src/services/task_service.py
- [X] T073 [P] [US4] Implement filter_by_status function in backend/src/services/task_service.py
- [X] T074 [P] [US4] Implement filter_by_priority function in backend/src/services/task_service.py
- [X] T075 [P] [US4] Implement filter_by_tags function with OR logic in backend/src/services/task_service.py
- [X] T076 [P] [US4] Implement sort_tasks function with dynamic ORDER BY in backend/src/services/task_service.py
- [X] T077 [US4] Extend get_tasks_for_user with search parameter in backend/src/services/task_service.py
- [X] T078 [US4] Extend get_tasks_for_user with status filter parameter in backend/src/services/task_service.py
- [X] T079 [US4] Extend get_tasks_for_user with priority filter parameter in backend/src/services/task_service.py
- [X] T080 [US4] Extend get_tasks_for_user with tags filter parameter in backend/src/services/task_service.py
- [X] T081 [US4] Extend get_tasks_for_user with sort_by parameter in backend/src/services/task_service.py
- [X] T082 [US4] Extend get_tasks_for_user with sort_order parameter in backend/src/services/task_service.py
- [X] T083 [US4] Handle null due_dates in sorting (place at end) in backend/src/services/task_service.py
- [X] T084 [US4] Add query parameters to GET /{user_id}/tasks endpoint in backend/src/api/tasks.py
- [X] T085 [US4] Validate query parameter values in backend/src/api/tasks.py
- [X] T086 [US4] Update getTasks API function with filter parameters in frontend/src/services/api.ts
- [X] T087 [US4] Create TaskFilters component in frontend/src/components/TaskFilters.tsx
- [X] T088 [US4] Add search input with debounce (300ms) in TaskFilters component
- [X] T089 [US4] Add status filter dropdown in TaskFilters component
- [X] T090 [US4] Add priority filter dropdown in TaskFilters component
- [X] T091 [US4] Add tag multi-select in TaskFilters component
- [X] T092 [US4] Add sort by dropdown in TaskFilters component
- [X] T093 [US4] Add sort order toggle in TaskFilters component
- [X] T094 [US4] Integrate TaskFilters with task list page in frontend/src/app/tasks/page.tsx

**Checkpoint**: At this point, User Stories 1-4 should all work independently

---

## Phase 7: User Story 5 - Recurring Tasks (Priority: P5)

**Goal**: Enable users to create recurring tasks that automatically generate future instances

**Independent Test**: Create recurring tasks with different frequencies, verify instance generation and duplicate prevention

### Implementation for User Story 5

- [X] T095 [P] [US5] Extend TaskBase model with is_recurring field in backend/src/models/task.py
- [X] T096 [P] [US5] Extend TaskBase model with recurrence_frequency field in backend/src/models/task.py
- [X] T097 [P] [US5] Extend Task model with last_recurrence_date field in backend/src/models/task.py
- [X] T098 [P] [US5] Update TaskCreate schema to include recurrence fields in backend/src/models/task.py
- [X] T099 [P] [US5] Update TaskRead schema to include recurrence fields in backend/src/models/task.py
- [X] T100 [P] [US5] Update TaskUpdate schema to include recurrence fields in backend/src/models/task.py
- [X] T101 [US5] Add recurrence validation (frequency required if is_recurring=true) in backend/src/models/task.py
- [X] T102 [US5] Implement calculate_next_due_date function in backend/src/services/task_service.py
- [X] T103 [US5] Implement should_generate_next_instance function in backend/src/services/task_service.py
- [X] T104 [US5] Implement generate_recurring_instance function in backend/src/services/task_service.py
- [X] T105 [US5] Add duplicate prevention logic using last_recurrence_date in backend/src/services/task_service.py
- [X] T106 [US5] Copy tags to new recurring instance in backend/src/services/task_service.py
- [X] T107 [US5] Update create_task_for_user to handle recurrence fields in backend/src/services/task_service.py
- [X] T108 [US5] Update update_task_by_id_and_user to handle recurrence fields in backend/src/services/task_service.py
- [X] T109 [US5] Add POST /{user_id}/tasks/{id}/generate-recurrence endpoint in backend/src/api/tasks.py
- [X] T110 [US5] Validate task is recurring in generate-recurrence endpoint in backend/src/api/tasks.py
- [X] T111 [US5] Handle errors for duplicate instances in generate-recurrence endpoint in backend/src/api/tasks.py
- [X] T112 [P] [US5] Add recurrence fields to Task type definition in frontend/src/types/index.ts
- [X] T113 [P] [US5] Add generateRecurrence API function in frontend/src/services/api.ts
- [X] T114 [US5] Add recurring checkbox to TaskForm in frontend/src/components/TaskForm.tsx
- [X] T115 [US5] Add recurrence frequency dropdown to TaskForm in frontend/src/components/TaskForm.tsx
- [X] T116 [US5] Show/hide frequency dropdown based on recurring checkbox in frontend/src/components/TaskForm.tsx
- [X] T117 [US5] Display recurring indicator icon in TaskList in frontend/src/components/TaskItem.tsx
- [X] T118 [US5] Add "Generate Next" button for recurring tasks in TaskList in frontend/src/components/TaskItem.tsx

**Checkpoint**: All user stories should now be independently functional

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T119 [P] Add error handling for invalid priority values across all endpoints
- [ ] T120 [P] Add error handling for invalid date formats across all endpoints
- [ ] T121 [P] Add error handling for invalid tag names across all endpoints
- [ ] T122 [P] Add error handling for invalid recurrence frequencies across all endpoints
- [ ] T123 [P] Verify user isolation for all new endpoints (cannot access other user's data)
- [ ] T124 [P] Add logging for priority operations in backend/src/services/task_service.py
- [ ] T125 [P] Add logging for tag operations in backend/src/services/tag_service.py
- [ ] T126 [P] Add logging for recurring task generation in backend/src/services/task_service.py
- [ ] T127 [P] Verify backward compatibility (existing tasks without new fields work correctly)
- [ ] T128 [P] Test performance of search/filter/sort with 1000 tasks (should be <1s)
- [ ] T129 [P] Verify all new fields have proper defaults
- [ ] T130 Update API documentation with new endpoints and parameters
- [ ] T131 Update README with new features description
- [ ] T132 Run quickstart.md validation to ensure all steps work

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4 → P5)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Builds on US1, US2, US3 but independently testable
- **User Story 5 (P5)**: Can start after Foundational (Phase 2) - Builds on US1, US2, US3 but independently testable

### Within Each User Story

- Tasks marked [P] can run in parallel (different files, no dependencies)
- Backend model changes before service changes
- Service changes before API endpoint changes
- Backend complete before frontend changes
- Frontend type definitions before component changes

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Within each user story, tasks marked [P] can run in parallel
- All Polish tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all parallel tasks for User Story 1 together:
Task T021: Extend TaskBase model with priority field
Task T022: Update TaskCreate schema
Task T023: Update TaskRead schema
Task T024: Update TaskUpdate schema
Task T031: Add priority field to Task type definition (frontend)

# Then sequential tasks:
Task T025: Add priority validation
Task T026: Update create_task_for_user
Task T027: Update update_task_by_id_and_user
# ... and so on
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Task Priority Management)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add User Story 5 → Test independently → Deploy/Demo
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Priority Management)
   - Developer B: User Story 2 (Due Dates)
   - Developer C: User Story 3 (Tags)
3. Stories complete and integrate independently
4. Then proceed to User Story 4 and 5

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- Tests are OPTIONAL - only add if explicitly requested in spec or by user

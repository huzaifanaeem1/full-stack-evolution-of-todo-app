# Quickstart Guide: Advanced and Intermediate Todo Features

**Feature**: 004-advanced-todo-features
**Date**: 2026-02-09
**Status**: Ready for Implementation

## Overview

This guide provides step-by-step instructions for implementing advanced todo features including priorities, tags, due dates, search/filter/sort, and recurring tasks. Follow the phases in order to ensure proper implementation.

## Prerequisites

- [x] Specification complete ([spec.md](./spec.md))
- [x] Implementation plan complete ([plan.md](./plan.md))
- [x] Research complete ([research.md](./research.md))
- [x] Data model defined ([data-model.md](./data-model.md))
- [x] API contracts defined ([contracts/](./contracts/))
- [ ] Development environment set up
- [ ] Database connection configured
- [ ] Existing Phase I-IV functionality operational

## Implementation Phases

### Phase 1: Database Schema Changes

**Goal**: Add new tables and columns to support advanced features

**Steps**:

1. **Create Alembic migration**:
   ```bash
   cd backend
   alembic revision -m "add_advanced_todo_features"
   ```

2. **Implement migration** (see [data-model.md](./data-model.md) for SQL):
   - Create `tag` table
   - Create `task_tag` association table
   - Add columns to `task` table: priority, due_date, is_recurring, recurrence_frequency, last_recurrence_date
   - Create indexes on new columns
   - Add constraints for data integrity

3. **Test migration**:
   ```bash
   # Apply migration
   alembic upgrade head

   # Verify schema
   psql $DATABASE_URL -c "\d task"
   psql $DATABASE_URL -c "\d tag"
   psql $DATABASE_URL -c "\d task_tag"

   # Test rollback
   alembic downgrade -1
   alembic upgrade head
   ```

4. **Verify backward compatibility**:
   - Existing tasks should still be accessible
   - All new fields should have defaults
   - No data loss on migration

**Acceptance Criteria**:
- [ ] Migration runs successfully without errors
- [ ] All tables and columns created with correct types
- [ ] Indexes created on priority, due_date, and tag relationships
- [ ] Constraints enforce data integrity
- [ ] Rollback works correctly
- [ ] Existing data remains intact

---

### Phase 2: Backend Models

**Goal**: Extend SQLModel entities with new fields and relationships

**Files to Modify/Create**:
- `backend/src/models/task.py` - EXTEND
- `backend/src/models/tag.py` - NEW
- `backend/src/models/task_tag.py` - NEW

**Steps**:

1. **Create PriorityLevel and RecurrenceFrequency enums**:
   ```python
   # backend/src/models/task.py
   from enum import Enum

   class PriorityLevel(str, Enum):
       HIGH = "high"
       MEDIUM = "medium"
       LOW = "low"

   class RecurrenceFrequency(str, Enum):
       DAILY = "daily"
       WEEKLY = "weekly"
       MONTHLY = "monthly"
   ```

2. **Extend Task model** (see [data-model.md](./data-model.md) for full definition):
   - Add priority field (default: MEDIUM)
   - Add due_date field (optional)
   - Add is_recurring field (default: False)
   - Add recurrence_frequency field (optional)
   - Add last_recurrence_date field (optional)
   - Add task_tags relationship

3. **Create Tag model**:
   - id, name, user_id, created_at
   - Add user and task_tags relationships

4. **Create TaskTag association model**:
   - task_id, tag_id (composite primary key)
   - Add task and tag relationships

5. **Update TaskCreate, TaskRead, TaskUpdate schemas**:
   - Add new fields to request/response models
   - Add tags array to TaskRead
   - Add validation for recurrence fields

**Acceptance Criteria**:
- [ ] All models defined with correct types
- [ ] Relationships configured correctly
- [ ] Enums defined and used
- [ ] Validation rules implemented
- [ ] Default values set appropriately

---

### Phase 3: Backend Services

**Goal**: Implement business logic for new features

**Files to Modify/Create**:
- `backend/src/services/task_service.py` - EXTEND
- `backend/src/services/tag_service.py` - NEW

**Steps**:

1. **Extend task_service.py**:

   a. **Update get_tasks_for_user** to support filtering and sorting:
   ```python
   async def get_tasks_for_user(
       user_id: UUID,
       db: AsyncSession,
       search: Optional[str] = None,
       status: Optional[str] = None,
       priority: Optional[PriorityLevel] = None,
       tags: Optional[List[str]] = None,
       sort_by: str = "created_at",
       sort_order: str = "desc"
   ) -> List[Task]:
       query = select(Task).where(Task.user_id == user_id)

       # Apply search filter
       if search:
           query = query.where(
               or_(
                   Task.title.ilike(f"%{search}%"),
                   Task.description.ilike(f"%{search}%")
               )
           )

       # Apply status filter
       if status == "completed":
           query = query.where(Task.is_completed == True)
       elif status == "pending":
           query = query.where(Task.is_completed == False)

       # Apply priority filter
       if priority:
           query = query.where(Task.priority == priority)

       # Apply tag filter (OR logic)
       if tags:
           query = query.join(TaskTag).join(Tag).where(Tag.name.in_(tags))

       # Apply sorting
       order_column = getattr(Task, sort_by)
       if sort_order == "desc":
           query = query.order_by(order_column.desc())
       else:
           query = query.order_by(order_column.asc())

       result = await db.execute(query)
       return result.scalars().all()
   ```

   b. **Update create_task_for_user** to handle tags:
   ```python
   async def create_task_for_user(
       task_data: TaskCreate,
       user_id: UUID,
       db: AsyncSession
   ) -> Task:
       # Create task
       task = Task(**task_data.dict(exclude={"tags"}), user_id=user_id)
       db.add(task)
       await db.flush()

       # Handle tags
       if task_data.tags:
           await assign_tags_to_task(task.id, task_data.tags, user_id, db)

       await db.commit()
       await db.refresh(task)
       return task
   ```

   c. **Add recurring task generation logic**:
   ```python
   async def generate_recurring_instance(
       task_id: UUID,
       user_id: UUID,
       db: AsyncSession
   ) -> Task:
       # Get parent task
       parent = await get_task_by_id_and_user(task_id, user_id, db)
       if not parent or not parent.is_recurring:
           raise ValueError("Task is not recurring")

       # Check if next instance already exists
       today = date.today()
       if parent.last_recurrence_date and parent.last_recurrence_date >= today:
           raise ValueError("Next instance already generated")

       # Calculate next due date
       next_due_date = calculate_next_due_date(
           parent.due_date,
           parent.recurrence_frequency
       )

       # Create new instance
       new_task = Task(
           user_id=user_id,
           title=parent.title,
           description=parent.description,
           priority=parent.priority,
           due_date=next_due_date,
           is_recurring=False,  # Instance is not recurring
           is_completed=False
       )
       db.add(new_task)

       # Copy tags
       tags = await get_tags_for_task(task_id, db)
       for tag in tags:
           task_tag = TaskTag(task_id=new_task.id, tag_id=tag.id)
           db.add(task_tag)

       # Update parent's last_recurrence_date
       parent.last_recurrence_date = today

       await db.commit()
       await db.refresh(new_task)
       return new_task
   ```

2. **Create tag_service.py**:
   ```python
   async def get_or_create_tag(
       name: str,
       user_id: UUID,
       db: AsyncSession
   ) -> Tag:
       # Try to find existing tag
       query = select(Tag).where(
           Tag.user_id == user_id,
           func.lower(Tag.name) == name.lower()
       )
       result = await db.execute(query)
       tag = result.scalar_one_or_none()

       if not tag:
           tag = Tag(name=name.strip(), user_id=user_id)
           db.add(tag)
           await db.flush()

       return tag

   async def assign_tags_to_task(
       task_id: UUID,
       tag_names: List[str],
       user_id: UUID,
       db: AsyncSession
   ):
       # Remove existing tags
       await db.execute(
           delete(TaskTag).where(TaskTag.task_id == task_id)
       )

       # Add new tags
       for name in tag_names:
           tag = await get_or_create_tag(name, user_id, db)
           task_tag = TaskTag(task_id=task_id, tag_id=tag.id)
           db.add(task_tag)

   async def get_tags_for_user(
       user_id: UUID,
       db: AsyncSession
   ) -> List[Dict]:
       query = select(
           Tag,
           func.count(TaskTag.task_id).label("task_count")
       ).where(
           Tag.user_id == user_id
       ).outerjoin(TaskTag).group_by(Tag.id)

       result = await db.execute(query)
       return [
           {"id": tag.id, "name": tag.name, "task_count": count, "created_at": tag.created_at}
           for tag, count in result.all()
       ]
   ```

**Acceptance Criteria**:
- [ ] Search filters tasks by title and description (case-insensitive)
- [ ] Status filter works for completed/pending
- [ ] Priority filter works for high/medium/low
- [ ] Tag filter uses OR logic (matches any tag)
- [ ] Sorting works for all supported fields
- [ ] Tags are created/reused correctly
- [ ] Recurring task generation creates proper instances
- [ ] Duplicate prevention works for recurring tasks

---

### Phase 4: Backend API Endpoints

**Goal**: Expose new features through REST API

**Files to Modify**:
- `backend/src/api/tasks.py` - EXTEND

**Steps**:

1. **Update GET /{user_id}/tasks endpoint**:
   ```python
   @tasks_router.get("/", response_model=List[TaskRead])
   async def get_user_tasks(
       user_id: UUID,
       db: Annotated[AsyncSession, Depends(get_async_db_session)],
       current_user: User = Depends(get_current_user),
       search: Optional[str] = None,
       status: Optional[str] = None,
       priority: Optional[PriorityLevel] = None,
       tags: Optional[List[str]] = Query(None),
       sort_by: str = "created_at",
       sort_order: str = "desc"
   ):
       if str(current_user.id) != str(user_id):
           raise HTTPException(status_code=403, detail="Access denied")

       tasks = await get_tasks_for_user(
           user_id, db, search, status, priority, tags, sort_by, sort_order
       )

       # Populate tags for each task
       for task in tasks:
           task.tags = await get_tag_names_for_task(task.id, db)

       return tasks
   ```

2. **Update POST /{user_id}/tasks endpoint**:
   - Handle tags in request body
   - Validate recurrence fields
   - Call extended create_task_for_user

3. **Update PUT /{user_id}/tasks/{id} endpoint**:
   - Handle tags in request body
   - Update task and tags atomically

4. **Add POST /{user_id}/tasks/{id}/generate-recurrence endpoint**:
   ```python
   @tasks_router.post("/{id}/generate-recurrence", response_model=TaskRead)
   async def generate_recurring_task(
       user_id: UUID,
       id: UUID,
       db: Annotated[AsyncSession, Depends(get_async_db_session)],
       current_user: User = Depends(get_current_user)
   ):
       if str(current_user.id) != str(user_id):
           raise HTTPException(status_code=403, detail="Access denied")

       try:
           new_task = await generate_recurring_instance(id, user_id, db)
           new_task.tags = await get_tag_names_for_task(new_task.id, db)
           return new_task
       except ValueError as e:
           raise HTTPException(status_code=400, detail=str(e))
   ```

5. **Add GET /{user_id}/tags endpoint** (optional):
   ```python
   @tasks_router.get("/tags", response_model=List[TagWithCount])
   async def get_user_tags(
       user_id: UUID,
       db: Annotated[AsyncSession, Depends(get_async_db_session)],
       current_user: User = Depends(get_current_user)
   ):
       if str(current_user.id) != str(user_id):
           raise HTTPException(status_code=403, detail="Access denied")

       return await get_tags_for_user(user_id, db)
   ```

**Acceptance Criteria**:
- [ ] All query parameters work correctly
- [ ] Request/response validation works
- [ ] Error handling returns appropriate status codes
- [ ] User isolation enforced on all endpoints
- [ ] Tags included in task responses
- [ ] Recurring task generation endpoint works

---

### Phase 5: Frontend Components

**Goal**: Update UI to support new features

**Files to Modify/Create**:
- `frontend/src/components/TaskForm.tsx` - EXTEND
- `frontend/src/components/TaskList.tsx` - EXTEND
- `frontend/src/components/TaskFilters.tsx` - NEW
- `frontend/src/lib/api.ts` - EXTEND

**Steps**:

1. **Extend TaskForm.tsx**:
   - Add priority dropdown (high/medium/low)
   - Add due date picker
   - Add tags input (comma-separated or tag chips)
   - Add recurring task checkbox and frequency dropdown
   - Update form submission to include new fields

2. **Extend TaskList.tsx**:
   - Display priority badge (color-coded)
   - Display due date (with overdue indicator)
   - Display tags as chips
   - Display recurring indicator icon
   - Add "Generate Next" button for recurring tasks

3. **Create TaskFilters.tsx**:
   - Search input
   - Status filter (all/completed/pending)
   - Priority filter (all/high/medium/low)
   - Tag filter (multi-select)
   - Sort by dropdown (title/priority/due_date/created_at)
   - Sort order toggle (asc/desc)

4. **Extend api.ts**:
   ```typescript
   export async function getTasks(
     userId: string,
     filters?: {
       search?: string;
       status?: string;
       priority?: string;
       tags?: string[];
       sort_by?: string;
       sort_order?: string;
     }
   ): Promise<Task[]> {
     const params = new URLSearchParams();
     if (filters?.search) params.append('search', filters.search);
     if (filters?.status) params.append('status', filters.status);
     if (filters?.priority) params.append('priority', filters.priority);
     if (filters?.tags) filters.tags.forEach(tag => params.append('tags', tag));
     if (filters?.sort_by) params.append('sort_by', filters.sort_by);
     if (filters?.sort_order) params.append('sort_order', filters.sort_order);

     const response = await fetch(
       `/api/${userId}/tasks?${params.toString()}`,
       { headers: { Authorization: `Bearer ${getToken()}` } }
     );
     return response.json();
   }
   ```

**Acceptance Criteria**:
- [ ] Task form includes all new fields
- [ ] Task list displays all new attributes
- [ ] Filters work and update task list
- [ ] Search is debounced (300ms delay)
- [ ] Tags are displayed as chips
- [ ] Priority is color-coded (red/yellow/green)
- [ ] Due dates show overdue indicator
- [ ] Recurring tasks show generation button

---

### Phase 6: Testing

**Goal**: Ensure all features work correctly

**Test Files to Create**:
- `backend/tests/integration/test_task_priority.py`
- `backend/tests/integration/test_task_tags.py`
- `backend/tests/integration/test_task_search.py`
- `backend/tests/integration/test_recurring_tasks.py`
- `frontend/tests/components/TaskFilters.test.tsx`

**Test Scenarios**:

1. **Priority Tests**:
   - Create task with each priority level
   - Update task priority
   - Filter tasks by priority
   - Sort tasks by priority

2. **Tag Tests**:
   - Create task with tags
   - Add/remove tags from task
   - Filter tasks by single tag
   - Filter tasks by multiple tags (OR logic)
   - Verify tag reuse across tasks

3. **Due Date Tests**:
   - Create task with due date
   - Update due date
   - Remove due date
   - Sort tasks by due date
   - Verify null dates sort to end

4. **Search Tests**:
   - Search by title
   - Search by description
   - Case-insensitive search
   - No results handling

5. **Recurring Task Tests**:
   - Create recurring task (daily/weekly/monthly)
   - Generate next instance
   - Verify duplicate prevention
   - Verify tag copying
   - Verify due date calculation

6. **Integration Tests**:
   - Combine multiple filters
   - Search + filter + sort
   - User isolation (cannot access other user's tasks/tags)

**Acceptance Criteria**:
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Test coverage >80%
- [ ] Edge cases covered
- [ ] User isolation verified

---

## Validation Checklist

Before marking implementation complete, verify:

- [ ] Database migration applied successfully
- [ ] All models defined and relationships working
- [ ] All service functions implemented
- [ ] All API endpoints working
- [ ] Frontend components updated
- [ ] All tests passing
- [ ] Backward compatibility maintained (existing tasks still work)
- [ ] User isolation enforced (cannot access other user's data)
- [ ] Performance acceptable (<1s for search/filter/sort)
- [ ] Error handling comprehensive
- [ ] API documentation updated
- [ ] No infrastructure changes made

---

## Common Issues & Solutions

### Issue: Tag filter returns no results
**Solution**: Verify JOIN query is correct and tags exist for user

### Issue: Recurring task creates duplicates
**Solution**: Check last_recurrence_date is being updated and duplicate check logic

### Issue: Search is slow
**Solution**: Add indexes on title and description columns

### Issue: Existing tasks missing new fields
**Solution**: Verify migration set proper defaults and fields are optional

### Issue: Frontend not displaying tags
**Solution**: Ensure tags are populated in API response (requires JOIN query)

---

## Next Steps

After implementation is complete:

1. Run `/sp.tasks` to generate detailed task list
2. Execute tasks in order (Setup → Foundational → User Stories)
3. Test each user story independently
4. Deploy to staging environment
5. Perform user acceptance testing
6. Deploy to production

---

## References

- [Feature Specification](./spec.md)
- [Implementation Plan](./plan.md)
- [Research Document](./research.md)
- [Data Model](./data-model.md)
- [API Contracts](./contracts/)

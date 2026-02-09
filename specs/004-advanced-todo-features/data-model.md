# Data Model: Advanced and Intermediate Todo Features

**Feature**: 004-advanced-todo-features
**Date**: 2026-02-09
**Status**: Complete

## Overview

This document defines the data entities, relationships, and validation rules for implementing advanced todo features. All entities maintain user isolation and backward compatibility with existing Phase I-IV functionality.

## Entity Definitions

### 1. Task (Extended)

**Description**: Extended version of existing Task entity with new organizational and automation fields.

**Table Name**: `task`

**Fields**:

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| id | UUID | PRIMARY KEY | uuid4() | Unique task identifier |
| user_id | UUID | FOREIGN KEY (user.id), NOT NULL | - | Owner of the task |
| title | VARCHAR(255) | NOT NULL | - | Task title |
| description | TEXT | NULLABLE | NULL | Task description |
| is_completed | BOOLEAN | NOT NULL | false | Completion status |
| priority | ENUM('high', 'medium', 'low') | NOT NULL | 'medium' | Task priority level |
| due_date | DATE | NULLABLE | NULL | Due date (no time component) |
| is_recurring | BOOLEAN | NOT NULL | false | Whether task recurs |
| recurrence_frequency | ENUM('daily', 'weekly', 'monthly') | NULLABLE | NULL | Recurrence pattern |
| last_recurrence_date | DATE | NULLABLE | NULL | Last generated instance date |
| created_at | TIMESTAMP | NOT NULL | now() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | now() | Last update timestamp |

**Indexes**:
- PRIMARY KEY: id
- INDEX: user_id
- INDEX: priority
- INDEX: due_date
- COMPOSITE INDEX: (user_id, priority)
- COMPOSITE INDEX: (user_id, due_date)

**Relationships**:
- BELONGS TO User (user_id → user.id)
- HAS MANY TaskTag (task.id → task_tag.task_id)
- HAS MANY Tag (through TaskTag)

**Validation Rules**:
- title: 1-255 characters, required
- description: 0-10000 characters, optional
- priority: must be 'high', 'medium', or 'low'
- due_date: valid ISO 8601 date (YYYY-MM-DD), optional
- recurrence_frequency: required if is_recurring=true, must be 'daily', 'weekly', or 'monthly'
- last_recurrence_date: must be <= current date if set

**Business Rules**:
- If is_recurring=false, recurrence_frequency and last_recurrence_date must be NULL
- If is_recurring=true, recurrence_frequency must be set
- User can only access/modify their own tasks (user_id isolation)
- Deleting a task cascades to TaskTag entries

**Backward Compatibility**:
- All new fields (priority, due_date, is_recurring, recurrence_frequency, last_recurrence_date) have defaults
- Existing queries without new fields continue to work
- Existing TaskCreate/TaskUpdate schemas remain valid

---

### 2. Tag (New)

**Description**: Categorization labels for organizing tasks. User-specific and reusable across multiple tasks.

**Table Name**: `tag`

**Fields**:

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| id | UUID | PRIMARY KEY | uuid4() | Unique tag identifier |
| name | VARCHAR(50) | NOT NULL | - | Tag name |
| user_id | UUID | FOREIGN KEY (user.id), NOT NULL | - | Owner of the tag |
| created_at | TIMESTAMP | NOT NULL | now() | Creation timestamp |

**Indexes**:
- PRIMARY KEY: id
- UNIQUE INDEX: (user_id, name) - prevents duplicate tag names per user
- INDEX: user_id
- INDEX: name

**Relationships**:
- BELONGS TO User (user_id → user.id)
- HAS MANY TaskTag (tag.id → task_tag.tag_id)
- HAS MANY Task (through TaskTag)

**Validation Rules**:
- name: 1-50 characters, required
- name: alphanumeric, spaces, hyphens, underscores only (regex: `^[a-zA-Z0-9 _-]+$`)
- name: case-sensitive (but unique constraint is case-insensitive)
- name: trimmed of leading/trailing whitespace

**Business Rules**:
- Tag names must be unique per user (case-insensitive)
- User can only access/modify their own tags (user_id isolation)
- Deleting a tag cascades to TaskTag entries (removes tag from all tasks)
- Tags with no associated tasks can be deleted
- Tags are automatically created when assigned to tasks (if not exists)

---

### 3. TaskTag (New)

**Description**: Many-to-many association table linking tasks to tags.

**Table Name**: `task_tag`

**Fields**:

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| task_id | UUID | FOREIGN KEY (task.id), NOT NULL | - | Reference to task |
| tag_id | UUID | FOREIGN KEY (tag.id), NOT NULL | - | Reference to tag |

**Indexes**:
- PRIMARY KEY: (task_id, tag_id) - composite primary key
- INDEX: task_id
- INDEX: tag_id

**Relationships**:
- BELONGS TO Task (task_id → task.id, ON DELETE CASCADE)
- BELONGS TO Tag (tag_id → tag.id, ON DELETE CASCADE)

**Validation Rules**:
- task_id: must reference existing task
- tag_id: must reference existing tag
- Composite primary key prevents duplicate associations

**Business Rules**:
- A task can have multiple tags
- A tag can be associated with multiple tasks
- Deleting a task removes all TaskTag entries for that task
- Deleting a tag removes all TaskTag entries for that tag
- User isolation enforced through Task and Tag entities

---

## Entity Relationships Diagram

```
┌─────────────────┐
│      User       │
│  (existing)     │
└────────┬────────┘
         │
         │ 1:N
         │
    ┌────▼─────────────────────────────────┐
    │           Task (Extended)            │
    │  ─────────────────────────────────   │
    │  + id: UUID                          │
    │  + user_id: UUID (FK)                │
    │  + title: VARCHAR(255)               │
    │  + description: TEXT                 │
    │  + is_completed: BOOLEAN             │
    │  + priority: ENUM (NEW)              │
    │  + due_date: DATE (NEW)              │
    │  + is_recurring: BOOLEAN (NEW)       │
    │  + recurrence_frequency: ENUM (NEW)  │
    │  + last_recurrence_date: DATE (NEW)  │
    │  + created_at: TIMESTAMP             │
    │  + updated_at: TIMESTAMP             │
    └────────┬─────────────────────────────┘
             │
             │ N:M (through TaskTag)
             │
    ┌────────▼─────────┐         ┌──────────────┐
    │     TaskTag      │◄────────┤     Tag      │
    │  (association)   │  N:1    │   (new)      │
    │  ───────────────│         │  ──────────  │
    │  + task_id: UUID │         │  + id: UUID  │
    │  + tag_id: UUID  │         │  + name: STR │
    └──────────────────┘         │  + user_id   │
                                 │  + created_at│
                                 └──────┬───────┘
                                        │
                                        │ N:1
                                        │
                                 ┌──────▼───────┐
                                 │     User     │
                                 │  (existing)  │
                                 └──────────────┘
```

---

## Database Migration Plan

### Migration: Add Advanced Todo Features

**Up Migration**:

```sql
-- Step 1: Create Tag table
CREATE TABLE tag (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL,
    user_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_user_tag UNIQUE (user_id, LOWER(name))
);

CREATE INDEX idx_tag_user_id ON tag(user_id);
CREATE INDEX idx_tag_name ON tag(name);

-- Step 2: Create TaskTag association table
CREATE TABLE task_tag (
    task_id UUID NOT NULL REFERENCES task(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES tag(id) ON DELETE CASCADE,
    PRIMARY KEY (task_id, tag_id)
);

CREATE INDEX idx_task_tag_task_id ON task_tag(task_id);
CREATE INDEX idx_task_tag_tag_id ON task_tag(tag_id);

-- Step 3: Add new columns to Task table
ALTER TABLE task
    ADD COLUMN priority VARCHAR(10) NOT NULL DEFAULT 'medium'
        CHECK (priority IN ('high', 'medium', 'low')),
    ADD COLUMN due_date DATE,
    ADD COLUMN is_recurring BOOLEAN NOT NULL DEFAULT false,
    ADD COLUMN recurrence_frequency VARCHAR(10)
        CHECK (recurrence_frequency IN ('daily', 'weekly', 'monthly')),
    ADD COLUMN last_recurrence_date DATE;

-- Step 4: Create indexes on new Task columns
CREATE INDEX idx_task_priority ON task(priority);
CREATE INDEX idx_task_due_date ON task(due_date);
CREATE INDEX idx_task_user_priority ON task(user_id, priority);
CREATE INDEX idx_task_user_due_date ON task(user_id, due_date);

-- Step 5: Add constraint for recurring tasks
ALTER TABLE task
    ADD CONSTRAINT check_recurring_frequency
    CHECK (
        (is_recurring = false AND recurrence_frequency IS NULL AND last_recurrence_date IS NULL)
        OR
        (is_recurring = true AND recurrence_frequency IS NOT NULL)
    );
```

**Down Migration**:

```sql
-- Step 1: Drop constraints
ALTER TABLE task DROP CONSTRAINT IF EXISTS check_recurring_frequency;

-- Step 2: Drop indexes
DROP INDEX IF EXISTS idx_task_user_due_date;
DROP INDEX IF EXISTS idx_task_user_priority;
DROP INDEX IF EXISTS idx_task_due_date;
DROP INDEX IF EXISTS idx_task_priority;
DROP INDEX IF EXISTS idx_task_tag_tag_id;
DROP INDEX IF EXISTS idx_task_tag_task_id;
DROP INDEX IF EXISTS idx_tag_name;
DROP INDEX IF EXISTS idx_tag_user_id;

-- Step 3: Drop new columns from Task
ALTER TABLE task
    DROP COLUMN IF EXISTS last_recurrence_date,
    DROP COLUMN IF EXISTS recurrence_frequency,
    DROP COLUMN IF EXISTS is_recurring,
    DROP COLUMN IF EXISTS due_date,
    DROP COLUMN IF EXISTS priority;

-- Step 4: Drop tables
DROP TABLE IF EXISTS task_tag;
DROP TABLE IF EXISTS tag;
```

---

## SQLModel Definitions

### Task Model (Extended)

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, date
from enum import Enum
import uuid

class PriorityLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class RecurrenceFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class TaskBase(SQLModel):
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=10000)
    is_completed: bool = Field(default=False)
    priority: PriorityLevel = Field(default=PriorityLevel.MEDIUM)
    due_date: Optional[date] = Field(default=None)
    is_recurring: bool = Field(default=False)
    recurrence_frequency: Optional[RecurrenceFrequency] = Field(default=None)

class Task(TaskBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    last_recurrence_date: Optional[date] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="tasks")
    task_tags: List["TaskTag"] = Relationship(back_populates="task")
```

### Tag Model

```python
class TagBase(SQLModel):
    name: str = Field(max_length=50, regex=r"^[a-zA-Z0-9 _-]+$")

class Tag(TagBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="tags")
    task_tags: List["TaskTag"] = Relationship(back_populates="tag")
```

### TaskTag Model

```python
class TaskTag(SQLModel, table=True):
    task_id: uuid.UUID = Field(foreign_key="task.id", primary_key=True)
    tag_id: uuid.UUID = Field(foreign_key="tag.id", primary_key=True)

    # Relationships
    task: Optional["Task"] = Relationship(back_populates="task_tags")
    tag: Optional["Tag"] = Relationship(back_populates="task_tags")
```

---

## API Request/Response Models

### TaskCreate (Extended)

```python
from pydantic import BaseModel, validator

class TaskCreate(TaskBase):
    tags: Optional[List[str]] = Field(default=[])

    @validator('recurrence_frequency')
    def validate_recurrence(cls, v, values):
        if values.get('is_recurring') and not v:
            raise ValueError('recurrence_frequency required when is_recurring=true')
        if not values.get('is_recurring') and v:
            raise ValueError('recurrence_frequency must be null when is_recurring=false')
        return v
```

### TaskRead (Extended)

```python
class TaskRead(TaskBase):
    id: uuid.UUID
    user_id: uuid.UUID
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime
```

### TaskUpdate (Extended)

```python
class TaskUpdate(SQLModel):
    title: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None, max_length=10000)
    is_completed: Optional[bool] = None
    priority: Optional[PriorityLevel] = None
    due_date: Optional[date] = None
    is_recurring: Optional[bool] = None
    recurrence_frequency: Optional[RecurrenceFrequency] = None
    tags: Optional[List[str]] = None
```

---

## Data Integrity Rules

1. **User Isolation**: All queries MUST filter by user_id
2. **Tag Uniqueness**: Tag names are unique per user (case-insensitive)
3. **Recurring Validation**: If is_recurring=true, recurrence_frequency must be set
4. **Cascade Deletes**: Deleting task/tag removes TaskTag associations
5. **Date Validation**: due_date and last_recurrence_date must be valid dates
6. **Priority Validation**: priority must be one of: high, medium, low
7. **Tag Name Validation**: alphanumeric, spaces, hyphens, underscores only

---

## Performance Considerations

**Indexes**:
- All foreign keys indexed
- Composite indexes on (user_id, priority) and (user_id, due_date) for common queries
- Tag name indexed for fast lookups

**Query Optimization**:
- Use JOIN for tag associations (avoid N+1 queries)
- Limit result sets with pagination
- Use SELECT with specific columns

**Expected Query Performance**:
- Task CRUD: <50ms
- Task list with filters: <200ms
- Tag operations: <50ms
- Search with filters: <1s (for 1000 tasks)

---

## References

- Feature Specification: [spec.md](./spec.md)
- Implementation Plan: [plan.md](./plan.md)
- Research Document: [research.md](./research.md)
- API Contracts: [contracts/](./contracts/)

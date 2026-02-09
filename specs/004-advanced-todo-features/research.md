# Research: Advanced and Intermediate Todo Features

**Feature**: 004-advanced-todo-features
**Date**: 2026-02-09
**Status**: Complete

## Purpose

This document captures technical research and decisions made during the planning phase for implementing advanced todo features including priorities, tags, due dates, search/filter/sort, and recurring tasks.

## Research Questions & Decisions

### 1. Priority Field Implementation

**Question**: How should task priorities be stored and validated?

**Options Considered**:
- String field with application-level validation
- Integer field (1=high, 2=medium, 3=low)
- Enum field with database-level constraint
- Separate priority table with foreign key

**Decision**: Enum field with database-level constraint

**Rationale**:
- Type safety at database level prevents invalid values
- SQLModel supports Python Enum types natively
- Clear, readable code (Priority.HIGH vs 1)
- No additional table joins required
- PostgreSQL CHECK constraint ensures data integrity

**Implementation Notes**:
```python
from enum import Enum

class PriorityLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

# In Task model:
priority: PriorityLevel = Field(default=PriorityLevel.MEDIUM)
```

---

### 2. Tag Storage and Relationships

**Question**: How should tags be stored and associated with tasks?

**Options Considered**:
- JSON array field in Task table
- Comma-separated string in Task table
- Separate Tag table with many-to-many relationship
- Tag table with one-to-many relationship (duplicate tags per task)

**Decision**: Separate Tag table with many-to-many relationship via TaskTag association table

**Rationale**:
- Normalized design prevents tag duplication
- Enables efficient tag-based queries with indexes
- Supports tag reuse across multiple tasks
- Allows future tag metadata (color, description, etc.)
- Standard relational pattern for many-to-many relationships
- User isolation enforced at Tag level (user_id foreign key)

**Implementation Notes**:
- Tag table: id, name, user_id, created_at
- TaskTag table: task_id, tag_id (composite primary key)
- Unique constraint on (user_id, name) in Tag table
- Cascade delete on task deletion removes TaskTag entries

---

### 3. Search Implementation Strategy

**Question**: What search mechanism should be used for keyword search?

**Options Considered**:
- PostgreSQL full-text search (tsvector, tsquery)
- PostgreSQL ILIKE pattern matching
- External search engine (Elasticsearch, Algolia)
- Application-level filtering after retrieval

**Decision**: PostgreSQL ILIKE for case-insensitive substring matching

**Rationale**:
- Simple implementation with no additional dependencies
- Sufficient for substring matching on title and description
- Case-insensitive by default (ILIKE operator)
- Performance acceptable for <1000 tasks per user
- No infrastructure changes required (per constitution)
- Can add indexes on title and description if needed

**Implementation Notes**:
```python
# Search query example:
query = query.where(
    or_(
        Task.title.ilike(f"%{search_term}%"),
        Task.description.ilike(f"%{search_term}%")
    )
)
```

**Limitations**:
- No fuzzy matching or typo tolerance
- No relevance scoring
- No phrase matching or boolean operators
- Acceptable trade-off for Phase V - Part A scope

---

### 4. Filter and Sort Query Building

**Question**: How should dynamic filtering and sorting be implemented?

**Options Considered**:
- Raw SQL with string concatenation
- SQLModel query builder with conditional clauses
- Query builder library (SQLAlchemy Core)
- Separate query methods for each filter combination

**Decision**: SQLModel query builder with dynamic WHERE clauses and ORDER BY

**Rationale**:
- Type-safe query construction
- Prevents SQL injection
- Composable filters (can combine multiple conditions)
- Leverages existing SQLModel ORM
- Clean, maintainable code
- Supports complex filter combinations

**Implementation Notes**:
```python
# Dynamic filter building:
query = select(Task).where(Task.user_id == user_id)

if search:
    query = query.where(or_(Task.title.ilike(f"%{search}%"), ...))
if priority:
    query = query.where(Task.priority == priority)
if tags:
    query = query.join(TaskTag).join(Tag).where(Tag.name.in_(tags))
if sort_by:
    order_column = getattr(Task, sort_by)
    query = query.order_by(order_column.desc() if sort_order == "desc" else order_column)
```

**Performance Considerations**:
- Add indexes on: priority, due_date, user_id
- Composite index on (user_id, priority) for common queries
- Index on Tag.name for tag filtering

---

### 5. Recurring Task Generation Logic

**Question**: How should recurring tasks be generated?

**Options Considered**:
- Background job (Celery, APScheduler) running on schedule
- Database trigger on task completion
- Synchronous generation on task completion
- Manual trigger endpoint
- Event-driven with message queue

**Decision**: Synchronous generation on task completion + manual trigger endpoint

**Rationale**:
- No background job infrastructure required (per constitution)
- No message queue infrastructure (Kafka prohibited)
- Simple, predictable behavior
- User has control via manual trigger
- Generates next instance when current instance completed
- Prevents duplicate generation with last_recurrence_date tracking

**Implementation Notes**:
```python
# On task completion:
if task.is_recurring and task.is_completed:
    if should_generate_next_instance(task):
        create_recurring_instance(task)

# Manual trigger endpoint:
POST /{user_id}/tasks/{id}/generate-recurrence
```

**Duplicate Prevention**:
- Track last_recurrence_date on parent task
- Check if next instance already exists before creating
- Use database transaction isolation

**Limitations**:
- No automatic generation at midnight/week start/month start
- Requires user action (completing task or manual trigger)
- Acceptable trade-off for no infrastructure changes

---

### 6. Due Date Storage Format

**Question**: How should due dates be stored?

**Options Considered**:
- PostgreSQL TIMESTAMP (with time component)
- PostgreSQL DATE (date only)
- String field (ISO 8601 format)
- Integer field (Unix timestamp)

**Decision**: PostgreSQL DATE type (date only, no time)

**Rationale**:
- Spec explicitly excludes time-of-day specifications
- Native database type with proper validation
- Efficient storage (4 bytes)
- Supports date arithmetic for recurring tasks
- ISO 8601 format (YYYY-MM-DD) in API
- Timezone-agnostic (dates are universal)

**Implementation Notes**:
```python
from datetime import date

# In Task model:
due_date: Optional[date] = Field(default=None)

# API validation:
from pydantic import validator

@validator('due_date')
def validate_due_date(cls, v):
    if v and not isinstance(v, date):
        raise ValueError('Invalid date format')
    return v
```

---

### 7. Tag Filtering Logic (AND vs OR)

**Question**: When filtering by multiple tags, should tasks match ALL tags or ANY tag?

**Options Considered**:
- AND logic (task must have all specified tags)
- OR logic (task must have at least one specified tag)
- Configurable via query parameter
- Separate endpoints for AND/OR

**Decision**: OR logic (task matches if it has ANY of the specified tags)

**Rationale**:
- Documented in spec assumptions
- More intuitive for discovery ("show me tasks tagged work OR urgent")
- Simpler query implementation
- Can be extended to support AND logic in future if needed

**Implementation Notes**:
```python
# OR logic query:
if tags:
    query = query.join(TaskTag).join(Tag).where(Tag.name.in_(tags))
```

---

### 8. Backward Compatibility Strategy

**Question**: How to ensure existing clients continue working?

**Options Considered**:
- API versioning (v1, v2 endpoints)
- Optional fields with defaults
- Separate endpoints for new features
- Feature flags

**Decision**: Optional fields with sensible defaults

**Rationale**:
- All new fields are optional in database schema
- Existing endpoints return same structure with additional optional fields
- Clients ignoring new fields continue working
- No API versioning complexity
- Aligns with constitution requirement for backward compatibility

**Implementation Notes**:
- priority: defaults to "medium"
- due_date: defaults to None (null)
- tags: defaults to empty array
- is_recurring: defaults to False
- Existing TaskCreate/TaskUpdate schemas extended with Optional fields

---

## Technology Stack Confirmation

**Backend**:
- FastAPI 0.104+ (existing)
- SQLModel 0.0.14+ (existing)
- Neon PostgreSQL driver (existing)
- Alembic for migrations (existing)
- Pydantic for validation (existing)

**Frontend**:
- Next.js 16+ with App Router (existing)
- React 18+ (existing)
- TypeScript 5.0+ (existing)
- Fetch API for HTTP requests (existing)

**No New Dependencies Required**: All features can be implemented with existing technology stack.

---

## Performance Considerations

**Database Indexes**:
- Add index on Task.priority
- Add index on Task.due_date
- Add composite index on (Task.user_id, Task.priority)
- Add index on Tag.name
- Add composite index on (Tag.user_id, Tag.name) for uniqueness

**Query Optimization**:
- Use SELECT with specific columns (avoid SELECT *)
- Limit result sets to reasonable page sizes
- Use JOIN instead of N+1 queries for tags
- Consider query result caching for common filters (future optimization)

**Expected Performance**:
- CRUD operations: <200ms (existing baseline)
- Search/filter/sort: <1s for 1000 tasks (within spec requirement)
- Tag operations: <100ms (simple lookups)

---

## Security Considerations

**User Isolation**:
- All queries MUST filter by user_id
- Tag table includes user_id foreign key
- TaskTag association inherits isolation from Task and Tag
- No cross-user tag visibility

**Input Validation**:
- Priority: enum validation (high/medium/low only)
- Due date: ISO 8601 format validation
- Tag names: alphanumeric, spaces, hyphens, underscores only
- Search terms: sanitized for SQL injection (ILIKE with parameterized queries)
- Recurrence frequency: enum validation (daily/weekly/monthly only)

**Authorization**:
- All endpoints require JWT authentication (existing)
- User ID extracted from JWT token (existing)
- Ownership validation before operations (existing pattern)

---

## Migration Strategy

**Database Migration Steps**:
1. Create Tag table with user_id foreign key
2. Create TaskTag association table
3. Add priority column to Task (default: 'medium')
4. Add due_date column to Task (nullable)
5. Add is_recurring column to Task (default: false)
6. Add recurrence_frequency column to Task (nullable)
7. Add last_recurrence_date column to Task (nullable)
8. Create indexes on new columns
9. Add unique constraint on (Tag.user_id, Tag.name)

**Rollback Plan**:
- Alembic downgrade removes all new columns and tables
- Existing data unaffected (new fields are optional)
- No data migration required (all new fields)

---

## Open Questions & Future Considerations

**Resolved**:
- ✅ Priority storage format
- ✅ Tag relationship design
- ✅ Search implementation
- ✅ Recurring task generation logic
- ✅ Due date format
- ✅ Tag filtering logic (OR vs AND)

**Future Enhancements** (out of scope for Phase V - Part A):
- Full-text search with relevance scoring
- Background job for automatic recurring task generation
- Advanced recurrence patterns (every 2 weeks, last day of month)
- Time-of-day for due dates
- Tag colors and metadata
- Task dependencies and subtasks
- Bulk operations

---

## References

- Feature Specification: [spec.md](./spec.md)
- Implementation Plan: [plan.md](./plan.md)
- SQLModel Documentation: https://sqlmodel.tiangolo.com/
- FastAPI Documentation: https://fastapi.tiangolo.com/
- PostgreSQL Documentation: https://www.postgresql.org/docs/

from sqlmodel import select, or_, and_
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import List, Optional
from uuid import UUID
from datetime import date, timedelta
import asyncio
from ..models.task import Task, TaskCreate, TaskUpdate, TaskPatch, PriorityLevel, RecurrenceFrequency
from ..models.task_tag import TaskTag
from ..models.tag import Tag
from .tag_service import assign_tags_to_task, get_tags_for_task
from .event_publisher import get_event_publisher
from ..config.dapr import (
    EVENT_TYPE_TASK_CREATED,
    EVENT_TYPE_TASK_UPDATED,
    EVENT_TYPE_TASK_COMPLETED,
    EVENT_TYPE_TASK_DELETED,
)


async def create_task_for_user(task_data: TaskCreate, user_id: UUID, db) -> Task:
    """Create a new task for a specific user"""
    # T026: Update create_task_for_user to handle priority and all new fields
    # T061: Extend create_task_for_user to handle tags
    # T031: Integrate EventPublisher for task.created events
    # Extract tags before creating task
    task_dict = task_data.dict(exclude_unset=True)
    tags = task_dict.pop('tags', None)

    # Create the task object with all fields except tags
    db_task = Task(
        **task_dict,
        user_id=user_id
    )

    try:
        db.add(db_task)
        await db.commit()
        await db.refresh(db_task)

        # Assign tags if provided
        if tags:
            await assign_tags_to_task(db_task.id, tags, user_id, db)
            # Populate tags for event payload
            tags_list = await get_tags_for_task(db_task.id, db)
            db_task.tags = [tag.name for tag in tags_list]
        else:
            db_task.tags = []

        # T031, T035: Publish task.created event asynchronously (non-blocking)
        # User operation succeeds regardless of event publishing result
        event_publisher = get_event_publisher()
        asyncio.create_task(
            event_publisher.publish_task_event(EVENT_TYPE_TASK_CREATED, db_task, user_id)
        )

        return db_task
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating task"
        )


async def get_tasks_for_user(
    user_id: UUID,
    db,
    search: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    tags: Optional[List[str]] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = None
) -> List[Task]:
    """Get all tasks for a specific user with optional search, filter, and sort"""
    # T063: Extend get_tasks_for_user to populate tags
    # T077-T082: Add search, filter, and sort parameters
    statement = select(Task).where(Task.user_id == user_id)

    # Apply filters
    statement = apply_search_filter(statement, search)
    statement = apply_status_filter(statement, status)
    statement = apply_priority_filter(statement, priority)
    statement = await apply_tags_filter(statement, tags, db)

    # Apply sorting
    statement = apply_sorting(statement, sort_by, sort_order)

    result = await db.execute(statement)
    tasks = result.scalars().all()

    # Populate tags for each task
    for task in tasks:
        tags_list = await get_tags_for_task(task.id, db)
        task.tags = [tag.name for tag in tags_list]

    return tasks


async def get_task_by_id_and_user(task_id: UUID, user_id: UUID, db) -> Optional[Task]:
    """Get a specific task by ID for a specific user"""
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    result = await db.execute(statement)
    task = result.scalar_one_or_none()
    return task


async def update_task_by_id_and_user(task_id: UUID, task_data: TaskUpdate, user_id: UUID, db) -> Optional[Task]:
    """Update a specific task by ID for a specific user"""
    # Get the existing task
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    result = await db.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        return None

    # T062: Extend update_task_by_id_and_user to handle tags
    # T032: Integrate EventPublisher for task.updated events
    # Extract tags before updating task
    update_data = task_data.dict(exclude_unset=True)
    tags = update_data.pop('tags', None)

    # Update the task with provided fields (except tags)
    for field, value in update_data.items():
        setattr(task, field, value)

    try:
        await db.commit()
        await db.refresh(task)

        # Update tags if provided
        if tags is not None:
            await assign_tags_to_task(task.id, tags, user_id, db)

        # Populate tags for event payload
        tags_list = await get_tags_for_task(task.id, db)
        task.tags = [tag.name for tag in tags_list]

        # T032, T035: Publish task.updated event asynchronously (non-blocking)
        event_publisher = get_event_publisher()
        asyncio.create_task(
            event_publisher.publish_task_event(EVENT_TYPE_TASK_UPDATED, task, user_id)
        )

        return task
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating task"
        )


async def patch_task_completion_status(task_id: UUID, task_patch: TaskPatch, user_id: UUID, db) -> Optional[Task]:
    """Update task completion status by ID for a specific user"""
    # T033: Integrate EventPublisher for task.completed events
    # Get the existing task
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    result = await db.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        return None

    # Update the completion status
    task.is_completed = task_patch.is_completed

    try:
        await db.commit()
        await db.refresh(task)

        # Populate tags for event payload
        tags_list = await get_tags_for_task(task.id, db)
        task.tags = [tag.name for tag in tags_list]

        # T033, T035: Publish task.completed event asynchronously if task is marked complete
        if task.is_completed:
            event_publisher = get_event_publisher()
            asyncio.create_task(
                event_publisher.publish_task_event(EVENT_TYPE_TASK_COMPLETED, task, user_id)
            )
        else:
            # If task is marked incomplete, publish task.updated event
            event_publisher = get_event_publisher()
            asyncio.create_task(
                event_publisher.publish_task_event(EVENT_TYPE_TASK_UPDATED, task, user_id)
            )

        return task
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating task completion status"
        )


async def delete_task_by_id_and_user(task_id: UUID, user_id: UUID, db) -> bool:
    """Delete a specific task by ID for a specific user"""
    # T034: Integrate EventPublisher for task.deleted events
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    result = await db.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        return False

    # Populate tags for event payload before deletion
    tags_list = await get_tags_for_task(task.id, db)
    task.tags = [tag.name for tag in tags_list]

    try:
        # T034, T035: Publish task.deleted event asynchronously before deletion
        # Store task data before deletion for event payload
        event_publisher = get_event_publisher()
        asyncio.create_task(
            event_publisher.publish_task_event(EVENT_TYPE_TASK_DELETED, task, user_id)
        )

        await db.delete(task)
        await db.commit()
        return True
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting task"
        )


# T072-T076: Search, filter, and sort helper functions for User Story 4

def apply_search_filter(statement, search: Optional[str]):
    """T072: Apply search filter with ILIKE on title and description"""
    if search and search.strip():
        search_pattern = f"%{search.strip()}%"
        statement = statement.where(
            or_(
                Task.title.ilike(search_pattern),
                Task.description.ilike(search_pattern)
            )
        )
    return statement


def apply_status_filter(statement, status: Optional[str]):
    """T073: Apply status filter (completed, active, all)"""
    if status == "completed":
        statement = statement.where(Task.is_completed == True)
    elif status == "active":
        statement = statement.where(Task.is_completed == False)
    # "all" or None means no filter
    return statement


def apply_priority_filter(statement, priority: Optional[str]):
    """T074: Apply priority filter"""
    if priority and priority in ["high", "medium", "low"]:
        statement = statement.where(Task.priority == priority)
    return statement


async def apply_tags_filter(statement, tags: Optional[List[str]], db):
    """T075: Apply tags filter with OR logic"""
    if tags and len(tags) > 0:
        # Get task IDs that have any of the specified tags
        tag_statement = select(TaskTag.task_id).join(Tag).where(
            Tag.name.in_([tag.lower().strip() for tag in tags])
        )
        result = await db.execute(tag_statement)
        task_ids = [row[0] for row in result.all()]

        if task_ids:
            statement = statement.where(Task.id.in_(task_ids))
        else:
            # No tasks match the tags, return empty result
            statement = statement.where(Task.id == None)

    return statement


def apply_sorting(statement, sort_by: Optional[str], sort_order: Optional[str]):
    """T076, T083: Apply sorting with dynamic ORDER BY, handling null due_dates"""
    if not sort_by:
        sort_by = "created_at"

    if sort_order not in ["asc", "desc"]:
        sort_order = "desc"

    # T083: Handle null due_dates in sorting (place at end)
    if sort_by == "due_date":
        if sort_order == "asc":
            # Nulls last for ascending
            statement = statement.order_by(Task.due_date.asc().nullslast())
        else:
            # Nulls last for descending
            statement = statement.order_by(Task.due_date.desc().nullslast())
    elif sort_by == "priority":
        # Priority order: high > medium > low
        priority_order = {"high": 1, "medium": 2, "low": 3}
        if sort_order == "asc":
            statement = statement.order_by(Task.priority.asc())
        else:
            statement = statement.order_by(Task.priority.desc())
    elif sort_by == "title":
        if sort_order == "asc":
            statement = statement.order_by(Task.title.asc())
        else:
            statement = statement.order_by(Task.title.desc())
    elif sort_by == "updated_at":
        if sort_order == "asc":
            statement = statement.order_by(Task.updated_at.asc())
        else:
            statement = statement.order_by(Task.updated_at.desc())
    else:  # created_at (default)
        if sort_order == "asc":
            statement = statement.order_by(Task.created_at.asc())
        else:
            statement = statement.order_by(Task.created_at.desc())

    return statement

# T102-T106: Recurring task generation functions for User Story 5

def calculate_next_due_date(current_due_date: date, frequency: RecurrenceFrequency) -> date:
    """T102: Calculate the next due date based on recurrence frequency"""
    if frequency == RecurrenceFrequency.DAILY:
        return current_due_date + timedelta(days=1)
    elif frequency == RecurrenceFrequency.WEEKLY:
        return current_due_date + timedelta(weeks=1)
    elif frequency == RecurrenceFrequency.MONTHLY:
        # Add approximately 30 days for monthly recurrence
        # More sophisticated logic could handle month-end edge cases
        return current_due_date + timedelta(days=30)
    else:
        raise ValueError(f"Invalid recurrence frequency: {frequency}")


def should_generate_next_instance(task: Task, today: date) -> bool:
    """T103: Check if a new recurring instance should be generated"""
    if not task.is_recurring or not task.recurrence_frequency:
        return False

    if not task.due_date:
        return False

    # T105: Duplicate prevention using last_recurrence_date
    if task.last_recurrence_date:
        # Check if we've already generated an instance for this period
        next_due = calculate_next_due_date(task.due_date, task.recurrence_frequency)
        if task.last_recurrence_date >= next_due:
            return False

    # Generate if the due date has passed
    return task.due_date <= today


async def generate_recurring_instance(task: Task, user_id: UUID, db) -> Task:
    """T104, T106: Generate a new instance of a recurring task with tags"""
    if not task.is_recurring or not task.recurrence_frequency or not task.due_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task is not recurring or missing required fields"
        )

    # T105: Check for duplicate prevention
    today = date.today()
    if not should_generate_next_instance(task, today):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Next instance has already been generated or due date has not passed"
        )

    # Calculate next due date
    next_due_date = calculate_next_due_date(task.due_date, task.recurrence_frequency)

    # T106: Get tags from original task to copy to new instance
    original_tags = await get_tags_for_task(task.id, db)
    tag_names = [tag.name for tag in original_tags]

    # Create new task instance
    new_task = Task(
        title=task.title,
        description=task.description,
        priority=task.priority,
        due_date=next_due_date,
        is_recurring=task.is_recurring,
        recurrence_frequency=task.recurrence_frequency,
        is_completed=False,  # New instance starts as incomplete
        user_id=user_id
    )

    try:
        db.add(new_task)
        await db.commit()
        await db.refresh(new_task)

        # T106: Copy tags to new recurring instance
        if tag_names:
            await assign_tags_to_task(new_task.id, tag_names, user_id, db)

        # Update original task's last_recurrence_date
        task.last_recurrence_date = next_due_date
        await db.commit()
        await db.refresh(task)

        return new_task
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating recurring task instance"
        )

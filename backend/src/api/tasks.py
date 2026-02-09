from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Annotated, List, Optional
from uuid import UUID
from ..models.task import Task, TaskCreate, TaskRead, TaskUpdate, TaskPatch
from ..models.tag import TagRead
from ..models.user import User
from ..services.task_service import (
    create_task_for_user,
    get_tasks_for_user,
    get_task_by_id_and_user,
    update_task_by_id_and_user,
    patch_task_completion_status,
    delete_task_by_id_and_user,
    generate_recurring_instance
)
from ..services.tag_service import get_tags_for_user
from ..services.auth import get_current_user
from ..config.database import get_db_session as get_async_db_session

tasks_router = APIRouter(prefix="/{user_id}/tasks", tags=["tasks"])

# T084, T085: Add query parameters to GET /{user_id}/tasks endpoint with validation
@tasks_router.get("/", response_model=List[TaskRead])
async def get_user_tasks(
    user_id: UUID,
    db: Annotated[AsyncSession, Depends(get_async_db_session)],
    current_user: User = Depends(get_current_user),
    search: Optional[str] = Query(None, description="Search in title and description"),
    status: Optional[str] = Query(None, regex="^(all|active|completed)$", description="Filter by status"),
    priority: Optional[str] = Query(None, regex="^(high|medium|low)$", description="Filter by priority"),
    tags: Optional[str] = Query(None, description="Comma-separated list of tags to filter by"),
    sort_by: Optional[str] = Query(None, regex="^(created_at|updated_at|due_date|priority|title)$", description="Sort by field"),
    sort_order: Optional[str] = Query(None, regex="^(asc|desc)$", description="Sort order")
):
    """Get all tasks for a specific user with optional search, filter, and sort"""
    # Verify that the user_id in the URL matches the authenticated user
    if str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied - cannot access another user's tasks"
        )

    # Parse tags from comma-separated string
    tags_list = None
    if tags:
        tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()]

    tasks = await get_tasks_for_user(
        user_id,
        db,
        search=search,
        status=status,
        priority=priority,
        tags=tags_list,
        sort_by=sort_by,
        sort_order=sort_order
    )
    return tasks


@tasks_router.post("/", response_model=TaskRead)
async def create_user_task(
    user_id: UUID,
    task_data: TaskCreate,
    db: Annotated[AsyncSession, Depends(get_async_db_session)],
    current_user: User = Depends(get_current_user)
):
    """Create a new task for a specific user"""
    # Verify that the user_id in the URL matches the authenticated user
    if str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied - cannot create tasks for another user"
        )

    # Create the task with the user_id from the URL to ensure consistency
    task = await create_task_for_user(task_data, user_id, db)
    return task


@tasks_router.get("/{id}", response_model=TaskRead)
async def get_user_task(
    user_id: UUID,
    id: UUID,
    db: Annotated[AsyncSession, Depends(get_async_db_session)],
    current_user: User = Depends(get_current_user)
):
    """Get a specific task by ID for a specific user"""
    # Verify that the user_id in the URL matches the authenticated user
    if str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied - cannot access another user's task"
        )

    task = await get_task_by_id_and_user(id, user_id, db)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task


@tasks_router.put("/{id}", response_model=TaskRead)
async def update_user_task(
    user_id: UUID,
    id: UUID,
    task_data: TaskUpdate,
    db: Annotated[AsyncSession, Depends(get_async_db_session)],
    current_user: User = Depends(get_current_user)
):
    """Update a specific task by ID for a specific user"""
    # Verify that the user_id in the URL matches the authenticated user
    if str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied - cannot update another user's task"
        )

    task = await update_task_by_id_and_user(id, task_data, user_id, db)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task


@tasks_router.patch("/{id}/complete", response_model=TaskRead)
async def update_task_completion(
    user_id: UUID,
    id: UUID,
    task_patch: TaskPatch,
    db: Annotated[AsyncSession, Depends(get_async_db_session)],
    current_user: User = Depends(get_current_user)
):
    """Update completion status of a specific task by ID for a specific user"""
    # Verify that the user_id in the URL matches the authenticated user
    if str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied - cannot update another user's task"
        )

    task = await patch_task_completion_status(id, task_patch, user_id, db)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task


@tasks_router.delete("/{id}")
async def delete_user_task(
    user_id: UUID,
    id: UUID,
    db: Annotated[AsyncSession, Depends(get_async_db_session)],
    current_user: User = Depends(get_current_user)
):
    """Delete a specific task by ID for a specific user"""
    # Verify that the user_id in the URL matches the authenticated user
    if str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied - cannot delete another user's task"
        )

    success = await delete_task_by_id_and_user(id, user_id, db)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return {"message": "Task deleted successfully"}


# T067: Add GET /{user_id}/tags endpoint
@tasks_router.get("/../tags", response_model=List[TagRead])
async def get_user_tags(
    user_id: UUID,
    db: Annotated[AsyncSession, Depends(get_async_db_session)],
    current_user: User = Depends(get_current_user)
):
    """Get all tags for a specific user"""
    # Verify that the user_id in the URL matches the authenticated user
    if str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied - cannot access another user's tags"
        )

    tags = await get_tags_for_user(user_id, db)
    return tags

# T109, T110, T111: Add POST /{user_id}/tasks/{id}/generate-recurrence endpoint
@tasks_router.post("/{id}/generate-recurrence", response_model=TaskRead)
async def generate_task_recurrence(
    user_id: UUID,
    id: UUID,
    db: Annotated[AsyncSession, Depends(get_async_db_session)],
    current_user: User = Depends(get_current_user)
):
    """Generate the next instance of a recurring task"""
    # Verify that the user_id in the URL matches the authenticated user
    if str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied - cannot generate recurrence for another user's task"
        )

    # Get the task
    task = await get_task_by_id_and_user(id, user_id, db)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # T110: Validate task is recurring
    if not task.is_recurring or not task.recurrence_frequency:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task is not recurring"
        )

    # T111: Handle errors for duplicate instances (handled in generate_recurring_instance)
    try:
        new_task = await generate_recurring_instance(task, user_id, db)
        return new_task
    except HTTPException as e:
        # Re-raise HTTP exceptions from the service layer
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recurring task instance: {str(e)}"
        )

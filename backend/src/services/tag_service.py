from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import List
from uuid import UUID
from ..models.tag import Tag, TagRead
from ..models.task_tag import TaskTag


# T054: Create get_or_create_tag function
async def get_or_create_tag(tag_name: str, user_id: UUID, db) -> Tag:
    """Get existing tag or create new one for a specific user"""
    # Normalize tag name (lowercase, stripped)
    normalized_name = tag_name.strip().lower()

    # Check if tag already exists for this user
    statement = select(Tag).where(
        Tag.user_id == user_id,
        Tag.name == normalized_name
    )
    result = await db.execute(statement)
    existing_tag = result.scalar_one_or_none()

    if existing_tag:
        return existing_tag

    # Create new tag
    new_tag = Tag(name=normalized_name, user_id=user_id)
    try:
        db.add(new_tag)
        await db.commit()
        await db.refresh(new_tag)
        return new_tag
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating tag"
        )


# T055: Implement assign_tags_to_task function
async def assign_tags_to_task(task_id: UUID, tag_names: List[str], user_id: UUID, db) -> List[Tag]:
    """Assign tags to a task, creating tags if they don't exist"""
    # First, remove all existing tags for this task
    delete_statement = select(TaskTag).where(TaskTag.task_id == task_id)
    result = await db.execute(delete_statement)
    existing_associations = result.scalars().all()

    for association in existing_associations:
        await db.delete(association)

    # Create or get tags and associate them with the task
    tags = []
    for tag_name in tag_names:
        if not tag_name or not tag_name.strip():
            continue

        tag = await get_or_create_tag(tag_name, user_id, db)
        tags.append(tag)

        # Create association
        task_tag = TaskTag(task_id=task_id, tag_id=tag.id)
        db.add(task_tag)

    try:
        await db.commit()
        return tags
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error assigning tags to task"
        )


# T056: Implement get_tags_for_task function
async def get_tags_for_task(task_id: UUID, db) -> List[Tag]:
    """Get all tags associated with a specific task"""
    statement = select(Tag).join(TaskTag).where(TaskTag.task_id == task_id)
    result = await db.execute(statement)
    tags = result.scalars().all()
    return list(tags)


# T057: Implement get_tags_for_user function
async def get_tags_for_user(user_id: UUID, db) -> List[Tag]:
    """Get all tags for a specific user"""
    statement = select(Tag).where(Tag.user_id == user_id).order_by(Tag.name)
    result = await db.execute(statement)
    tags = result.scalars().all()
    return list(tags)

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
import uuid
from pydantic import validator
import re


# T051: Create TagBase schema
class TagBase(SQLModel):
    name: str = Field(max_length=50)

    # T053: Add tag name validation (alphanumeric, spaces, hyphens, underscores)
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Tag name cannot be empty')

        # Allow alphanumeric, spaces, hyphens, underscores
        if not re.match(r'^[a-zA-Z0-9\s\-_]+$', v):
            raise ValueError('Tag name can only contain letters, numbers, spaces, hyphens, and underscores')

        # Normalize: strip and convert to lowercase for consistency
        return v.strip().lower()


# T049: Create Tag model
class Tag(TagBase, table=True):
    __tablename__ = "tags"  # Use existing table name

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to user
    user: Optional["User"] = Relationship(back_populates="tags")


# T052: Create TagRead schema
class TagRead(TagBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True

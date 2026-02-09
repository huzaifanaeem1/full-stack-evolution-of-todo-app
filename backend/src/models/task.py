from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, date
import uuid
from pydantic import BaseModel
from enum import Enum


# T006: Create PriorityLevel enum
class PriorityLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# T007: Create RecurrenceFrequency enum
class RecurrenceFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


# T021: Extend TaskBase model with priority field
# T035: Extend TaskBase model with due_date field
# T095: Extend TaskBase model with is_recurring field
# T096: Extend TaskBase model with recurrence_frequency field
class TaskBase(SQLModel):
    title: str
    description: Optional[str] = None
    is_completed: bool = Field(default=False)
    priority: PriorityLevel = Field(default=PriorityLevel.MEDIUM)
    due_date: Optional[date] = Field(default=None)
    is_recurring: bool = Field(default=False)
    recurrence_frequency: Optional[RecurrenceFrequency] = Field(default=None)


# T097: Extend Task model with last_recurrence_date field
class Task(TaskBase, table=True):
    __tablename__ = "tasks"  # Use existing table name

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    last_recurrence_date: Optional[date] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to user
    user: Optional["User"] = Relationship(back_populates="tasks")


# T022, T036, T098: Update TaskCreate schema to include optional priority, due_date, and recurrence fields
# T025, T039, T101: Add validation for priority, due_date, and recurrence fields
# T058: Update TaskCreate schema to include optional tags array
class TaskCreate(TaskBase):
    priority: Optional[PriorityLevel] = Field(default=PriorityLevel.MEDIUM)
    due_date: Optional[date] = Field(default=None)
    is_recurring: Optional[bool] = Field(default=False)
    recurrence_frequency: Optional[RecurrenceFrequency] = Field(default=None)
    tags: Optional[List[str]] = Field(default=None)

    # T101: Add recurrence validation (frequency required if is_recurring=true)
    @validator('recurrence_frequency')
    def validate_recurrence(cls, v, values):
        is_recurring = values.get('is_recurring', False)
        if is_recurring and not v:
            raise ValueError('recurrence_frequency is required when is_recurring is true')
        if not is_recurring and v:
            raise ValueError('recurrence_frequency should not be set when is_recurring is false')
        return v

    class Config:
        use_enum_values = True


# T023, T037, T099: Update TaskRead schema to include priority, due_date, and recurrence fields
# T059: Update TaskRead schema to include tags array
class TaskRead(TaskBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    tags: List[str] = Field(default_factory=list)

    class Config:
        use_enum_values = True


# T024, T038, T100: Update TaskUpdate schema to include optional priority, due_date, and recurrence fields
# T060: Update TaskUpdate schema to include optional tags array
class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    priority: Optional[PriorityLevel] = None
    due_date: Optional[date] = None
    is_recurring: Optional[bool] = None
    recurrence_frequency: Optional[RecurrenceFrequency] = None
    tags: Optional[List[str]] = None

    class Config:
        use_enum_values = True


class TaskPatch(BaseModel):
    is_completed: Optional[bool] = None
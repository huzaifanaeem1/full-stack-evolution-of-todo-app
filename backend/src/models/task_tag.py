from sqlmodel import SQLModel, Field
import uuid


# T050: Create TaskTag association model
class TaskTag(SQLModel, table=True):
    __tablename__ = "task_tags"  # Use existing table name

    task_id: uuid.UUID = Field(foreign_key="tasks.id", primary_key=True)
    tag_id: uuid.UUID = Field(foreign_key="tags.id", primary_key=True)

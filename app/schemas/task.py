from datetime import date
from pydantic import BaseModel, Field
from typing import Optional


class TaskCreate(BaseModel):
    task_description: str = Field(
        description="Описание задачи",
        max_length=300
    )
    assignee: str
    due_date: Optional[date] = Field(default=None)


class TaskRead(TaskCreate):
    task_id: int

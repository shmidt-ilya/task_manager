from datetime import date, timedelta
from pydantic import BaseModel, Field
from typing import Optional


class TaskCreate(BaseModel):
    task_description: str = Field(
        description="Описание задачи",
        max_length=300
    )
    assignee: str
    due_date: Optional[date] = Field(
        default_factory=lambda: date.today() + timedelta(days=1)
    )


class TaskRead(TaskCreate):
    task_id: int

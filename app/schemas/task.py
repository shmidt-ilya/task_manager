from datetime import date
from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    task_description: str = Field(
        description="Описание задачи",
        max_length=300
    )
    assignee: str
    due_date: date


class TaskRead(TaskCreate):
    task_id: int

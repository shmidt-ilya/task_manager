from datetime import date
from pydantic import BaseModel


class TaskBase(BaseModel):
    task_description: str
    assignee: str
    due_date: date


class TaskWithId(TaskBase):
    task_id: int

from datetime import date
from pydantic import BaseModel


class TaskCreate(BaseModel):
    task_description: str
    assignee: str
    due_date: date


class TaskRead(BaseModel):
    task_id: int
    task_description: str
    assignee: str
    due_date: date

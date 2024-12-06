from datetime import date, timedelta
from pydantic import BaseModel, Field, BeforeValidator
from typing import Optional, Annotated, TypeAlias
from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel, Field as SQLField


def _empty_str_or_none(value: str | None) -> None:
    if value is None or value == "":
        return None
    raise ValueError("Expected empty value")


EmptyStrOrNone: TypeAlias = Annotated[None, BeforeValidator(_empty_str_or_none)]


class TaskCreate(BaseModel):
    task_description: str = Field(
        description="Описание задачи",
        max_length=300
    )
    assignee: str
    due_date: Optional[date] = Field(
        description="Крайний срок исполнения задачи. "
                    "Не допускаются даты, более ранние, "
                    "чем сегодняшняя.",
        gt=date.today() - timedelta(days=1),
        default_factory=lambda: date.today() + timedelta(days=1)
    )


class TaskRead(TaskCreate):
    task_id: int
    due_date: EmptyStrOrNone | date


class User(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("email"),)
    user_id: int = SQLField(default=None, nullable=False, primary_key=True)
    email: str = SQLField(nullable=True, unique_items=True)
    password: str | None
    name: str


class Project(SQLModel, table=True):
    project_id: int = SQLField(default=None, nullable=False, primary_key=True)
    project_name: str
    project_description: str | None


class Task(SQLModel, TaskRead, table=True):
    task_id: int = SQLField(default=None, nullable=False, primary_key=True)
    due_date: date
    assignee: int = SQLField(foreign_key="user.user_id")
    project: int = SQLField(default=None, nullable=True, foreign_key="project.project_id")

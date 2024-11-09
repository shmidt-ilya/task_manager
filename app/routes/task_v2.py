from fastapi import APIRouter, status, Depends
from sqlalchemy import text
from sqlmodel import Session, select, SQLModel
from app.db import get_session, engine
from ..schemas import task as schema_task
from typing import Annotated
from ..api_docs import request_examples

router = APIRouter(prefix="/v2/tasks", tags=["Tasks"])


@router.get("/test-db", status_code=status.HTTP_200_OK)
def test_database(session: Session = Depends(get_session)):
    result = session.exec(select(text("'Hello world'"))).all()
    return result


@router.get("/create-db-tables",
            status_code=status.HTTP_200_OK)
def test_database():
    SQLModel.metadata.create_all(engine)
    return {"message": "Tables created"}


@router.post("/", status_code=status.HTTP_201_CREATED,
             response_model=schema_task.TaskRead,
             summary = 'Добавить задачу')
def create_task(task: Annotated[
                        schema_task.TaskCreate,
                        request_examples.example_create_task
                ],
                session: Session = Depends(get_session)):
    """
    Добавить задачу.
    """
    new_task = schema_task.Task(
        task_description=task.task_description,
        assignee=task.assignee,
        due_date=task.due_date
    )
    session.add(new_task)
    session.commit()
    session.refresh(new_task)
    return new_task
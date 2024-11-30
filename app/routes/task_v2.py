from fastapi import APIRouter, status, Depends, HTTPException
from sqlmodel import Session, select
from app.db import get_session
from ..schemas import task as schema_task
from typing import Annotated, List
from ..api_docs import request_examples

router = APIRouter(prefix="/v2/tasks", tags=["Управление задачами в БД"])


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


@router.get("/", status_code=status.HTTP_200_OK,
            response_model=List[schema_task.TaskRead])
def read_tasks(session: Session = Depends(get_session)):
    tasks = session.exec(select(schema_task.Task)).all()
    if tasks is None or len(tasks) == 0:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail=f"The task list is empty."
        )
    return tasks


@router.get("/{task_id}", response_model=schema_task.TaskRead)
def read_task_by_id(task_id: int):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=f"Unable to read task with ID {task_id}: "
               f"method is not implemented yet."
    )


@router.patch("/{task_id}", status_code=status.HTTP_200_OK, response_model=schema_task.TaskRead)
def update_task_by_id(task_id: int, data_for_update: dict):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=f"Unable to update task with ID {task_id}: "
               f"method is not implemented yet."
    )


@router.delete("/{task_id}", status_code=status.HTTP_200_OK)
def delete_task_by_id(task_id: int):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=f"Unable to delete task with ID {task_id}: "
               f"method is not implemented yet."
    )

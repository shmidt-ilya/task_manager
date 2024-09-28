from fastapi import APIRouter, status, HTTPException
from ..schemas import task as schema_task
from typing import List
from app.data_handler import write_task_to_csv, read_tasks_from_csv

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", status_code=status.HTTP_201_CREATED,
             response_model=schema_task.TaskRead)
def create_task(task: schema_task.TaskCreate):
    new_task = write_task_to_csv(task)
    return new_task


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[schema_task.TaskRead])
def read_tasks():
    tasks = read_tasks_from_csv()
    if tasks is None:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail=f"test"
        )
    return tasks

from fastapi import APIRouter, status
from ..schemas import task as schema_task
from app.data_handler import write_task_to_csv

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", status_code=status.HTTP_201_CREATED,
             response_model=schema_task.TaskRead)
def create_task(task: schema_task.TaskCreate):
    new_task = write_task_to_csv(task)
    return new_task

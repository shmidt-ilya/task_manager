from fastapi import APIRouter, status, HTTPException, Depends
from sqlmodel import Session
from typing import List, Annotated
from app.data_handler import (write_task_to_csv, read_tasks_from_csv,
                              read_task_from_csv, update_task_in_csv)
from ..api_docs import request_examples
from ..db import get_session
from ..schemas.task import Task, TaskCreate, TaskRead
from ..schemas.employee import Employee
from ..services.workload_service import WorkloadService
from ..auth.auth_handler import get_current_user

router = APIRouter(prefix="/v1/tasks", tags=["Управление задачами в файле"])


@router.post("/", status_code=status.HTTP_201_CREATED,
             response_model=TaskRead,
             summary = 'Добавить задачу')
def create_task(
    task: TaskCreate,
    session: Session = Depends(get_session),
    current_user: Employee = Depends(get_current_user)
):
    """
    Добавить задачу.
    """
    workload_service = WorkloadService(session)
    
    # Проверяем, может ли сотрудник взять задачу
    if not workload_service.get_employee_workload(task.assignee).can_take_task(task.complexity):
        # Ищем другого сотрудника
        new_assignee = workload_service.find_available_employee(task.complexity)
        if new_assignee:
            task.assignee = new_assignee.employee_id
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No available employees can take this task"
            )

    db_task = Task.from_orm(task)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    
    # Обновляем загруженность сотрудника
    workload_service.update_employee_workload(db_task.assignee, db_task.complexity)
    
    return db_task


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[TaskRead])
def read_tasks(
    session: Session = Depends(get_session),
    current_user: Employee = Depends(get_current_user)
):
    tasks = session.query(Task).all()
    if tasks is None:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail=f"The task list is empty."
        )
    return tasks


@router.get("/{task_id}", response_model=TaskRead)
def read_task(
    task_id: int,
    session: Session = Depends(get_session),
    current_user: Employee = Depends(get_current_user)
):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    return task


@router.patch("/{task_id}", status_code=status.HTTP_200_OK, response_model=TaskRead)
def update_task_by_id(task_id: int, data_for_update: dict):
    task_fields = set(TaskCreate.model_fields.keys())

    if not set(data_for_update.keys()) <= task_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"An update request must only contain one or more of the following fields: {', '.join(task_fields)}."
        )

    task = update_task_in_csv(task_id, data_for_update)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )

    return task


@router.delete("/{task_id}", status_code=status.HTTP_200_OK)
def delete_task_by_id(task_id: int):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=f"Unable to delete task with ID {task_id}: "
               f"method is not implemented yet."
    )


@router.put("/{task_id}/reassign")
def reassign_task(
    task_id: int,
    session: Session = Depends(get_session),
    current_user: Employee = Depends(get_current_user)
):
    workload_service = WorkloadService(session)
    new_assignee = workload_service.reassign_task(task_id)
    
    if not new_assignee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No available employees can take this task"
        )
    
    return {"message": f"Task reassigned to employee {new_assignee.employee_id}"}


@router.get("/employee/{employee_id}/workload")
def get_employee_workload(
    employee_id: int,
    session: Session = Depends(get_session),
    current_user: Employee = Depends(get_current_user)
):
    workload_service = WorkloadService(session)
    try:
        workload = workload_service.get_employee_workload(employee_id)
        return {
            "employee_id": employee_id,
            "current_tasks": workload.current_tasks,
            "total_complexity": workload.total_complexity,
            "workload_percentage": workload.workload_percentage
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

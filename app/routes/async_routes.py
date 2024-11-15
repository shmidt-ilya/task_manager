from fastapi import APIRouter, status, Depends, HTTPException
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_async_session
from ..schemas import task as schema_task
from typing import List

router = APIRouter(prefix="/v2/async", tags=["Асинхронные операции"])


@router.get("/tasks", status_code=status.HTTP_200_OK,
            response_model=List[schema_task.TaskRead])
async def read_tasks_async(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(schema_task.Task))
    tasks = result.scalars().all()
    if tasks is None or len(tasks) == 0:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail=f"The task list is empty."
        )
    return tasks

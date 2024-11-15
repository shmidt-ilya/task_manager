from fastapi import FastAPI
from app.routes import (task, task_v2, utils, async_routes)
from contextlib import asynccontextmanager
from app.db import init_database

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_database()
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Система управления задачами",
    description="Простейшая система управления задачами, основанная на "
                "фреймворке FastAPI.",
    version="0.0.1",
    contact={
        "name": "Цифровая кафедра МФТИ",
        "url": "https://mipt.ru",
        "email": "digitaldepartments@mipt.ru",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    }
)

app.include_router(task.router)
app.include_router(task_v2.router)
app.include_router(utils.router)
app.include_router(async_routes.router)

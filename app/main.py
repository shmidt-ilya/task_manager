from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import (task, task_v2, utils, auth, employee)
from contextlib import asynccontextmanager
from app.db import init_database
from app.init_db import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализация базы данных при запуске
    init_database()
    init_db()
    yield

app = FastAPI(
    lifespan=lifespan,
    title="Система управления задачами",
    description="Система управления задачами с учетом загруженности сотрудников и их квалификации. "
                "Позволяет автоматически распределять задачи между сотрудниками на основе их текущей "
                "загруженности и уровня квалификации. Основана на фреймворке FastAPI.",
    version="0.0.1"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(task.router)
app.include_router(task_v2.router)
app.include_router(utils.router)
app.include_router(auth.router)
app.include_router(employee.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Task Manager API"}

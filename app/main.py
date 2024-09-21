from fastapi import FastAPI
from app.routes import task

app = FastAPI()


app.include_router(task.router)

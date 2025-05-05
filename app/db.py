from sqlmodel import create_engine, Session, SQLModel
import os

# Создаем директорию для базы данных, если она не существует
os.makedirs("data", exist_ok=True)

# Создаем подключение к SQLite
DB_URL = "sqlite:///data/taskman.db"
engine = create_engine(DB_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

def init_database():
    SQLModel.metadata.create_all(engine)

from app.config import settings as cnf
from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

DB_URL = f"postgresql://{cnf.db_username}:{cnf.db_password}@{cnf.db_host}:{cnf.db_port}/{cnf.db_name}"
ASYNC_DB_URL = f"postgresql+asyncpg://{cnf.db_username}:{cnf.db_password}@{cnf.db_host}:{cnf.db_port}/{cnf.db_name}"
engine = create_engine(DB_URL, echo=True)
async_engine = create_async_engine(ASYNC_DB_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session


async_session = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


async def get_async_session() -> AsyncSession:
    """
    Используется для внедрения новых сессий в маршруты в качестве зависимости
    через механизм Dependency Injection.
    """
    async with async_session() as session:
        yield session


def init_database():
    SQLModel.metadata.create_all(engine)

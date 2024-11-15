from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

DB_URL = "postgresql://fastapi_taskman:fastapi_taskman@127.0.0.1:5432/fastapi_taskman"
ASYNC_DB_URL = "postgresql+asyncpg://fastapi_taskman:fastapi_taskman@127.0.0.1:5432/fastapi_taskman"
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

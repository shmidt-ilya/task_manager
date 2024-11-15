from fastapi import APIRouter, status, Depends
from sqlalchemy import text
from sqlmodel import Session, select, SQLModel
from app.db import get_session, engine

router = APIRouter(prefix="/utils", tags=["Utils"])


@router.get("/test-db", status_code=status.HTTP_200_OK)
def test_database(session: Session = Depends(get_session)):
    result = session.exec(select(text("'Hello world'"))).all()
    return result


@router.get("/create-db-tables",
            status_code=status.HTTP_200_OK)
def test_database():
    SQLModel.metadata.create_all(engine)
    return {"message": "Tables created"}

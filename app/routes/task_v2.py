from fastapi import APIRouter, status, Depends
from sqlalchemy import text
from sqlmodel import Session, select
from app.db import get_session

router = APIRouter(prefix="/v2/tasks", tags=["Tasks"])


@router.get("/test-db", status_code=status.HTTP_200_OK)
def test_database(session: Session = Depends(get_session)):
    result = session.exec(select(text("'Hello world'"))).all()
    return result

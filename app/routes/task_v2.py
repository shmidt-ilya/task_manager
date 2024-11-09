from fastapi import APIRouter, status, Depends
from sqlalchemy import text
from sqlmodel import Session
from app.db import get_session

router = APIRouter(prefix="/v2/tasks", tags=["Tasks"])


@router.get("/testdb", status_code=status.HTTP_200_OK)
def test_database(session: Session = Depends(get_session)):
    sql = text("""
        SELECT 'Hello', 'world'
    """)
    result = session.execute(sql).fetchall()
    return dict(result)

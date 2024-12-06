from fastapi import APIRouter, status, Depends, HTTPException
from sqlmodel import Session
from app.db import get_session
from ..schemas import task as schema_task
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation


router = APIRouter(prefix="/auth", tags=["Безопасность"])


@router.post("/signup", status_code=status.HTTP_201_CREATED,
             response_model=schema_task.User,
             summary = 'Добавить пользователя')
def create_user(user: schema_task.User,
                session: Session = Depends(get_session)):
    new_user = schema_task.User(
        name=user.name,
        email=user.email,
        password=user.password
    )
    try:
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user
    except IntegrityError as e:
        assert isinstance(e.orig, UniqueViolation)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"User with email {user.email} already exists"
        )

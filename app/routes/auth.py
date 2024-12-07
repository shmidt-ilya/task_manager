from fastapi import APIRouter, status, Depends, HTTPException
from sqlmodel import Session, select
from app.db import get_session
from ..schemas import task as schema_task
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from ..auth import auth_handler


router = APIRouter(prefix="/auth", tags=["Безопасность"])

@router.post("/signup", status_code=status.HTTP_201_CREATED,
             response_model=schema_task.User,
             summary = 'Добавить пользователя')
def create_user(user: schema_task.User,
                session: Session = Depends(get_session)):
    new_user = schema_task.User(
        name=user.name,
        email=user.email,
        password=auth_handler.get_password_hash(user.password)
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


@router.post("/login", status_code=status.HTTP_200_OK)
def user_login(login_attempt_data: OAuth2PasswordRequestForm = Depends(),
               db_session: Session = Depends(get_session)):
    statement = (select(schema_task.User)
                 .where(schema_task.User.email == login_attempt_data.username))
    existing_user = db_session.exec(statement).first()

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"User {login_attempt_data.username} not found"
        )

    if existing_user.password == login_attempt_data.password:
    if auth_handler.verify_password(
            login_attempt_data.password,
            existing_user.password):
        access_token = auth_handler.create_access_token(
            existing_user.user_id)
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Wrong password for user {login_attempt_data.username}"
        )

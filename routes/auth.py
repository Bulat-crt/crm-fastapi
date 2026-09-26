from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from data_base import get_db
from dependencies import get_current_user
from schemas import UserRegister, UserResponse
from models import User
from services.auth_service import register_user, authenticate_user, create_access_token

router = APIRouter()

@router.post("/auth/register", status_code=201, response_model=UserResponse)
def register(user: UserRegister, session: Session = Depends(get_db)):
  
    new_user = register_user(
        session=session,
        name=user.name,
        email=user.email,   
        password=user.password
    )

    if not new_user:
        raise HTTPException(
            status_code=409,
            detail="Пользователь с таким email уже существует"
        )

    return new_user

@router.post("/auth/login")
def login(form: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_db)):

    logined_user = authenticate_user(session=session, email=form.username, password=form.password)

    if not logined_user:
        raise HTTPException(
            status_code=401,
            detail="Неверный email или пароль"
        )

    access_token = create_access_token(logined_user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/users/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from models import User
from schemas import UserCreate, UserResponse, UserLogin, Token, UserUpdatePassword
from connection import get_session
from auth import get_password_hash, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, session: Session = Depends(get_session)):
    """Регистрация нового пользователя"""
    # Проверяем, существует ли пользователь
    existing_user = session.exec(
        select(User).where(User.username == user.username)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    existing_email = session.exec(
        select(User).where(User.email == user.email)
    ).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Создаём нового пользователя
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.post("/login", response_model=Token)
def login(user: UserLogin, session: Session = Depends(get_session)):
    """Авторизация и получение JWT токена"""
    # Ищем пользователя
    db_user = session.exec(
        select(User).where(User.username == user.username)
    ).first()

    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    # Создаём токен
    access_token = create_access_token(data={"sub": str(db_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Получить информацию о текущем пользователе"""
    return current_user


@router.get("/", response_model=List[UserResponse])
def get_users(
        current_user: User = Depends(get_current_user),
        session: Session = Depends(get_session)
):
    """Получить список всех пользователей (только для авторизованных)"""
    users = session.exec(select(User)).all()
    return users


@router.put("/change-password")
def change_password(
        password_data: UserUpdatePassword,
        current_user: User = Depends(get_current_user),
        session: Session = Depends(get_session)
):
    """Смена пароля"""
    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect old password")

    current_user.hashed_password = get_password_hash(password_data.new_password)
    session.add(current_user)
    session.commit()
    return {"message": "Password changed successfully"}
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from models import User


def create_user(
    session: Session,
    name: str,
    email: str,
    password_hash: str,
    role: str
) -> User:

    user = User(
        name=name,
        email=email,
        password_hash=password_hash,
        role=role
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


def get_user_by_id(session: Session, user_id: int) -> User | None:
    statement = select(User).where(User.id == user_id)
    user = session.scalars(statement).first()

    return user

def get_user_by_email(session: Session, user_email: str) -> User | None:
    statement = select(User).where(User.email == user_email)
    user = session.scalars(statement).first()

    return user

def update_user(session: Session, user_id: int, name: str, email: str):
    statement = select(User).where(User.id == user_id)
    user = session.scalars(statement).first()
    if not user:
        return False
    user.name = name
    user.email = email
    session.commit()
    return True

def delete_user(session: Session, user_id: int):
    statement = select(User).where(User.id == user_id)
    user = session.scalars(statement).first()
    if not user:
        return False

    session.delete(user)
    session.commit()
    return True

def get_all_users_from_bd(session: Session, offset: int, limit: int):
    statement = select(User).offset(offset).limit(limit)
    total_statement = select(func.count()).select_from(User)
    users = session.scalars(statement).all()
    total = session.scalar(total_statement)
    return users, total

def change_role(session: Session, role: str, user_id):
    statement = select(User).where(User.id == user_id)
    user = session.scalars(statement).first()
    if not user:
        return False

    user.role = role
    session.commit()

    return user

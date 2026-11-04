from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from jose import jwt, JWTError
from models import User
from enums.role import Role
from config import settings
from datetime import datetime, timedelta, timezone
from repositories.user_repository import create_user, get_user_by_email

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expire
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

def decode_access_token(token: str) -> int:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Недействительный токен"
            )

        return int(user_id)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен"
        )


def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)  

def register_user(
    session: Session,
    name: str,
    email: str,
    password: str
):
    existing_user = get_user_by_email(session, email)

    if existing_user:
        return False

    password_hash = hash_password(password)

    return create_user(
        session=session,
        name=name,
        email=email,
        password_hash=password_hash,
        role=Role.MANAGER
    )

def authenticate_user(
    session: Session,
    email: str,
    password: str
) -> User | None:
    existing_user = get_user_by_email(session, email)

    if not existing_user:
        return None

    password_hash = existing_user.password_hash
    password_true = verify_password(password, password_hash)
    if password_true:
        return existing_user
    return None


    
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from core.settings import settings
import jwt
from app.database import get_db
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from app.schemas.token import TokenData
from app.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def verify_password(plain_password, password_hash):
    return pwd_context.verify(plain_password, password_hash)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user(db: AsyncSession, username: str) -> User | None:
    """
    Fetches a user from the database by their email (username).
    """
    query = select(User).where(User.email == username)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def authenticate_user(
    db: AsyncSession, username: str, password: str
) -> User | None:
    """
    Authenticates a user. Returns the user object on success, None otherwise.
    """
    normalized_username = username.lower().strip()
    user = await get_user(db, normalized_username)

    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None

    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = await get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

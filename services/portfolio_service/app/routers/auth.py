from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, FastAPI, HTTPException, status, APIRouter
from app.models import User
from core.security import (
    authenticate_user,
    get_current_user,
    create_access_token,
)
from datetime import datetime, timedelta
from core.settings import settings
from app.schemas.token import Token
from app.schemas.users import UserInDB
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession


ACCESS_TOKEN_EXPIRES_MIN = settings.ACCESS_TOKEN_EXPIRES_MIN

router = APIRouter()


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db),
) -> Token:
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRES_MIN)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/users/me/", response_model=UserInDB)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user


@router.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]

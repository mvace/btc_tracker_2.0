from pydantic import BaseModel, EmailStr, constr
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: constr(min_length=8)


class UserRead(BaseModel):
    id: int
    email: EmailStr
    username: str

    model_config = {"from_attributes": True}


class UserInDB(UserRead):
    password_hash: str
    disabled: bool = False


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

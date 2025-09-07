from pydantic import BaseModel, EmailStr, constr, field_validator
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: constr(min_length=8)

    @field_validator("email")
    def email_to_lower(cls, value):
        """Converts email to lowercase before validation."""
        return value.lower()


class UserRead(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

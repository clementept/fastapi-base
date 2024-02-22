from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserCreateSchema(BaseModel):
    email: EmailStr
    password: str


class UserResponseSchema(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    activation_code: str | None
    created_at: datetime
    updated_at: datetime | None
    is_admin: bool

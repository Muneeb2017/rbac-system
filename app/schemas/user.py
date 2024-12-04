from app.models.role import Role
from pydantic import BaseModel, EmailStr # type: ignore
from typing import List, Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class User(UserBase):
    id: int
    is_active: bool
    roles: List["Role"]

    class Config:
        from_attributes = True
from app.models.permission import Permission
from pydantic import BaseModel # type: ignore
from typing import List, Optional

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    pass

class Role(RoleBase):
    id: int
    permissions: List["Permission"]

    class Config:
        from_attributes = True
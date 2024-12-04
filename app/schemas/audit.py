from pydantic import BaseModel # type: ignore
from typing import Optional, Dict, Any
from datetime import datetime

class AuditLogBase(BaseModel):
    action: str
    resource: str
    resource_id: Optional[str] = None
    access_granted: bool
    ip_address: Optional[str] = None
    request_method: str
    request_path: str
    request_body: Optional[Dict[str, Any]] = None
    response_status: int
    additional_details: Optional[Dict[str, Any]] = None

class AuditLogCreate(AuditLogBase):
    pass

class AuditLogResponse(AuditLogBase):
    id: int
    user_id: int
    timestamp: datetime
    username: Optional[str] = None  # Added for response convenience

    class Config:
        from_attributes = True

class AuditLogFilter(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    user_id: Optional[int] = None
    action: Optional[str] = None
    resource: Optional[str] = None
    access_granted: Optional[bool] = None
    response_status: Optional[int] = None
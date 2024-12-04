from fastapi import APIRouter, Depends, HTTPException, status # type: ignore
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import role as role_models
from ..schemas import role as role_schemas
from ..utils.auth import get_current_user, validate_access
from ..utils.audit_logger import log_access_attempt

router = APIRouter(prefix="/roles", tags=["roles"])

@router.get("/", response_model=List[role_schemas.Role])
async def read_roles(
    db: Session = Depends(get_db),
    current_user: role_models.User = Depends(get_current_user)
):
    if not validate_access(current_user, "roles", "read", db):
        log_access_attempt(db, current_user, "read", "roles", False)
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    roles = db.query(role_models.Role).all()
    log_access_attempt(db, current_user, "read", "roles", True)
    return roles

@router.get("/{role_id}", response_model=role_schemas.Role)
async def read_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: role_models.User = Depends(get_current_user)
):
    if not validate_access(current_user, "roles", "read", db):
        log_access_attempt(db, current_user, "read", "roles", False)
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    role = db.query(role_models.Role).filter(role_models.Role.id == role_id).first()
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    
    log_access_attempt(db, current_user, "read", "roles", True)
    return role

@router.put("/{role_id}/permissions")
async def assign_permissions_to_role(
    role_id: int,
    permission_ids: List[int],
    db: Session = Depends(get_db),
    current_user: role_models.User = Depends(get_current_user)
):
    # Only admin can assign permissions
    is_admin = any(role.name == "admin" for role in current_user.roles)
    if not is_admin:
        log_access_attempt(db, current_user, "update", "roles", False)
        raise HTTPException(status_code=403, detail="Only admin can assign permissions")
    
    role = db.query(role_models.Role).filter(role_models.Role.id == role_id).first()
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    
    permissions = db.query(role_models.Permission)\
        .filter(role_models.Permission.id.in_(permission_ids))\
        .all()
    
    role.permissions = permissions
    db.commit()
    
    log_access_attempt(db, current_user, "update", "roles", True, "Assigned permissions to role")
    return {"message": "Permissions assigned successfully"}
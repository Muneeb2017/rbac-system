from fastapi import APIRouter, Depends, HTTPException, status # type: ignore
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import permission as permission_models
from ..schemas import permission as permission_schemas
from ..utils.auth import get_current_user, validate_access
from ..utils.audit_logger import log_access_attempt

router = APIRouter(prefix="/permissions", tags=["permissions"])

@router.get("/", response_model=List[permission_schemas.Permission])
async def read_permissions(
    db: Session = Depends(get_db),
    current_user: permission_models.User = Depends(get_current_user)
):
    if not validate_access(current_user, "permissions", "read", db):
        log_access_attempt(db, current_user, "read", "permissions", False)
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    permissions = db.query(permission_models.Permission).all()
    log_access_attempt(db, current_user, "read", "permissions", True)
    return permissions

@router.post("/", response_model=permission_schemas.Permission)
async def create_permission(
    permission: permission_schemas.PermissionCreate,
    db: Session = Depends(get_db),
    current_user: permission_models.User = Depends(get_current_user)
):
    # Only admin can create permissions
    is_admin = any(role.name == "admin" for role in current_user.roles)
    if not is_admin:
        log_access_attempt(db, current_user, "create", "permissions", False)
        raise HTTPException(status_code=403, detail="Only admin can create permissions")
    
    db_permission = permission_models.Permission(**permission.dict())
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    
    log_access_attempt(db, current_user, "create", "permissions", True)
    return db_permission

@router.get("/role/{role_id}", response_model=List[permission_schemas.Permission])
async def read_role_permissions(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: permission_models.User = Depends(get_current_user)
):
    if not validate_access(current_user, "permissions", "read", db):
        log_access_attempt(db, current_user, "read", "permissions", False)
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    role = db.query(permission_models.Role).filter(permission_models.Role.id == role_id).first()
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    
    log_access_attempt(db, current_user, "read", "permissions", True)
    return role.permissions
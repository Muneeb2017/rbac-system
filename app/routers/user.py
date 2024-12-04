from fastapi import APIRouter, Depends, HTTPException # type: ignore
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import user as user_models
from ..schemas import user as user_schemas
from ..utils.auth import get_password_hash, get_current_user, validate_access
from ..utils.audit_logger import log_access_attempt

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=user_schemas.User)
async def create_user(
    user: user_schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user)
):
    # Validate if current user has permission to create users
    if not validate_access(current_user, "users", "create", db):
        log_access_attempt(db, current_user, "create", "users", False)
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Check if user already exists
    db_user = db.query(user_models.User).filter(
        user_models.User.username == user.username
    ).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = user_models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    log_access_attempt(db, current_user, "create", "users", True)
    return db_user

@router.get("/", response_model=List[user_schemas.User])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user)
):
    if not validate_access(current_user, "users", "read", db):
        log_access_attempt(db, current_user, "read", "users", False)
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    users = db.query(user_models.User).offset(skip).limit(limit).all()
    log_access_attempt(db, current_user, "read", "users", True)
    return users

@router.get("/{user_id}", response_model=user_schemas.User)
async def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user)
):
    if not validate_access(current_user, "users", "read", db):
        log_access_attempt(db, current_user, "read", "users", False)
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db_user = db.query(user_models.User).filter(user_models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    log_access_attempt(db, current_user, "read", "users", True)
    return db_user

@router.put("/{user_id}/roles")
async def assign_role_to_user(
    user_id: int,
    role_ids: List[int],
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user)
):
    if not validate_access(current_user, "users", "update", db):
        log_access_attempt(db, current_user, "update", "users", False)
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db_user = db.query(user_models.User).filter(user_models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Clear existing roles and assign new ones
    roles = db.query(user_models.Role).filter(user_models.Role.id.in_(role_ids)).all()
    db_user.roles = roles
    db.commit()
    
    log_access_attempt(db, current_user, "update", "users", True, "Assigned roles to user")
    return {"message": "Roles assigned successfully"}
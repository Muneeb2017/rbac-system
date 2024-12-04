from fastapi import FastAPI, Depends, HTTPException, status # type: ignore
from fastapi.security import OAuth2PasswordRequestForm # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from sqlalchemy.orm import Session
from datetime import timedelta
from .database import get_db, engine
from .models import user, role, permission, audit
from .routers import user, role, permission, audit
from .utils.auth import verify_password, create_access_token
from .config import get_settings

# Create database tables
user.Base.metadata.create_all(bind=engine)
role.Base.metadata.create_all(bind=engine)
permission.Base.metadata.create_all(bind=engine)
audit.Base.metadata.create_all(bind=engine)

settings = get_settings()
app = FastAPI(title="RBAC System API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user.router)
app.include_router(role.router)
app.include_router(permission.router)
app.include_router(audit.router)

@app.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(user.User).filter(user.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/validate-access")
async def validate_user_access(
    resource: str,
    action: str,
    db: Session = Depends(get_db),
    current_user: user.User = Depends(get_current_user) # type: ignore
):
    has_access = any(
        permission.resource == resource and permission.action == action
        for role in current_user.roles
        for permission in role.permissions
    )
    
    # Log the access attempt
    log_access_attempt( # type: ignore
        db=db,
        user=current_user,
        action=action,
        resource=resource,
        access_granted=has_access
    )
    
    return {"has_access": has_access}

@app.get("/")
async def root():
    return {
        "message": "RBAC System API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }
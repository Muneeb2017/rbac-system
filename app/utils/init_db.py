from sqlalchemy.orm import Session
from ..models.role import Role
from ..models.permission import Permission
from ..models.user import User
from ..utils.auth import get_password_hash

def init_db(db: Session):
    # Create default roles if they don't exist
    roles = {
        "admin": "Full system access",
        "supervisor": "Supervisor access with limited administrative capabilities",
        "staff": "Basic staff access"
    }

    default_roles = {}
    for role_name, description in roles.items():
        role = db.query(Role).filter(Role.name == role_name).first()
        if not role:
            role = Role(name=role_name, description=description)
            db.add(role)
            db.commit()
            db.refresh(role)
        default_roles[role_name] = role

    # Create default permissions
    permissions = [
        # User permissions
        {"name": "create_user", "description": "Create new users", "resource": "users", "action": "create"},
        {"name": "read_user", "description": "View user details", "resource": "users", "action": "read"},
        {"name": "update_user", "description": "Update user details", "resource": "users", "action": "update"},
        
        # Role permissions
        {"name": "read_role", "description": "View roles", "resource": "roles", "action": "read"},
        {"name": "update_role", "description": "Update role permissions", "resource": "roles", "action": "update"},
        
        # Permission permissions
        {"name": "create_permission", "description": "Create new permissions", "resource": "permissions", "action": "create"},
        {"name": "read_permission", "description": "View permissions", "resource": "permissions", "action": "read"},
        
        # API access permissions
        {"name": "access_api_one", "description": "Access API One", "resource": "api_one", "action": "access"},
        {"name": "access_api_two", "description": "Access API Two", "resource": "api_two", "action": "access"},
        {"name": "access_api_three", "description": "Access API Three", "resource": "api_three", "action": "access"}
    ]

    for perm_data in permissions:
        perm = db.query(Permission).filter(Permission.name == perm_data["name"]).first()
        if not perm:
            perm = Permission(**perm_data)
            db.add(perm)
            db.commit()
            db.refresh(perm)

    # Assign permissions to roles
    admin_role = default_roles["admin"]
    supervisor_role = default_roles["supervisor"]
    staff_role = default_roles["staff"]

    # Get all permissions
    all_permissions = db.query(Permission).all()
    admin_role.permissions = all_permissions

    # Supervisor gets all except role and permission management
    supervisor_permissions = [p for p in all_permissions 
                            if not any(x in p.name for x in ["update_role", "create_permission"])]
    supervisor_role.permissions = supervisor_permissions

    # Staff gets basic access
    staff_permissions = [p for p in all_permissions 
                        if p.name in ["read_user", "access_api_one", "access_api_two"]]
    staff_role.permissions = staff_permissions

    db.commit()

    # Create default admin user if it doesn't exist
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            is_active=True
        )
        admin_user.roles = [admin_role]
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

if __name__ == "__main__":
    from ..database import SessionLocal
    db = SessionLocal()
    try:
        init_db(db)
        print("Database initialized successfully!")
    finally:
        db.close()
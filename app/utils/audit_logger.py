from sys import audit
from sqlalchemy.orm import Session
from ..models.audit import AuditLog
from ..models.user import User

def log_access_attempt(
    db: Session,
    user: User,
    action: str,
    resource: str,
    access_granted: bool,
    details: str = None
):
    audit_log = AuditLog(
        user_id=user.id,
        action=action,
        resource=resource,
        access_granted=access_granted,
        details=details
    )
    db.add(audit_log)
    db.commit()
    return audit
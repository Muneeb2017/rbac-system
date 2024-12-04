import csv
from io import StringIO

from django.http import StreamingHttpResponse
from numpy import ufunc
from fastapi import APIRouter, Depends, HTTPException, Query, Request # type: ignore
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime, timedelta
from ..database import get_db
from ..models import audit as audit_models
from ..schemas import audit as audit_schemas
from ..utils.auth import get_current_user, validate_access
from ..models.user import User

router = APIRouter(prefix="/audit", tags=["audit"])







@router.get("/logs", response_model=List[audit_schemas.AuditLogResponse])
async def get_audit_logs(
    request: Request,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    resource: Optional[str] = Query(None),
    access_granted: Optional[bool] = Query(None),
    response_status: Optional[int] = Query(None),
    page: int = Query(1, gt=0),
    limit: int = Query(50, gt=0, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve audit logs with various filtering options.
    Only users with appropriate permissions can access this endpoint.
    """
    if not validate_access(current_user, "audit_logs", "read", db):
        raise HTTPException(status_code=403, detail="Not enough permissions to access audit logs")

    query = db.query(audit_models.AuditLog)

    # Apply filters
    if start_date:
        query = query.filter(audit_models.AuditLog.timestamp >= start_date)
    if end_date:
        query = query.filter(audit_models.AuditLog.timestamp <= end_date)
    if user_id:
        query = query.filter(audit_models.AuditLog.user_id == user_id)
    if action:
        query = query.filter(audit_models.AuditLog.action == action)
    if resource:
        query = query.filter(audit_models.AuditLog.resource == resource)
    if access_granted is not None:
        query = query.filter(audit_models.AuditLog.access_granted == access_granted)
    if response_status:
        query = query.filter(audit_models.AuditLog.response_status == response_status)

    # Add pagination
    total = query.count()
    query = query.order_by(audit_models.AuditLog.timestamp.desc())\
                 .offset((page - 1) * limit)\
                 .limit(limit)

    logs = query.all()

    # Add username to response
    for log in logs:
        if hasattr(log, 'user') and log.user:
            log.username = log.user.username

    return logs

#for example, 
## Get all failed access attempts in the last 24 hours
#GET /audit/logs?start_date=2024-03-03T00:00:00&access_granted=false

@router.get("/logs/summary")
async def get_audit_logs_summary(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a summary of audit logs including:
    - Total number of access attempts
    - Number of successful/failed attempts
    - Most accessed resources
    - Most common response statuses
    """
    if not validate_access(current_user, "audit_logs", "read", db):
        raise HTTPException(status_code=403, detail="Not enough permissions to access audit logs")

    query = db.query(audit_models.AuditLog)

    if start_date:
        query = query.filter(audit_models.AuditLog.timestamp >= start_date)
    if end_date:
        query = query.filter(audit_models.AuditLog.timestamp <= end_date)

    total_attempts = query.count()
    successful_attempts = query.filter(audit_models.AuditLog.access_granted == True).count()
    failed_attempts = query.filter(audit_models.AuditLog.access_granted == False).count()

    # Get most accessed resources
    resource_access = db.query(
        audit_models.AuditLog.resource,
        ufunc.count(audit_models.AuditLog.id).label('count')
    ).group_by(audit_models.AuditLog.resource)\
     .order_by(ufunc.count(audit_models.AuditLog.id).desc())\
     .limit(5)\
     .all()

    return {
        "total_attempts": total_attempts,
        "successful_attempts": successful_attempts,
        "failed_attempts": failed_attempts,
        "success_rate": (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0,
        "most_accessed_resources": [
            {"resource": r[0], "count": r[1]} for r in resource_access
        ]
    }

@router.get("/logs/export")
async def export_audit_logs(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    format: str = Query("csv", regex="^(csv|json)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Export audit logs in CSV or JSON format
    """
    if not validate_access(current_user, "audit_logs", "export", db):
        raise HTTPException(status_code=403, detail="Not enough permissions to export audit logs")

    query = db.query(audit_models.AuditLog)
    if start_date:
        query = query.filter(audit_models.AuditLog.timestamp >= start_date)
    if end_date:
        query = query.filter(audit_models.AuditLog.timestamp <= end_date)

    logs = query.all()
    
    if format == "csv":
        # Create CSV content
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "ID", "Timestamp", "User ID", "Action", "Resource",
            "Access Granted", "IP Address", "Request Method",
            "Response Status"
        ])
        
        for log in logs:
            writer.writerow([
                log.id, log.timestamp, log.user_id, log.action,
                log.resource, log.access_granted, log.ip_address,
                log.request_method, log.response_status
            ])
        
        return StreamingHttpResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=audit_logs_{datetime.now()}.csv"}
        )
    else:
        return {"logs": [audit_schemas.AuditLogResponse.from_orm(log) for log in logs]}
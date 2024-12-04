from datetime import datetime
from fastapi import Request, Response # type: ignore
from starlette.middleware.base import BaseHTTPMiddleware # type: ignore
from starlette.types import Message # type: ignore
from typing import Callable
import json
from ..database import SessionLocal
from ..models.audit import AuditLog
from ..utils.auth import get_current_user

class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Start timing the request
        start_time = datetime.utcnow()
        
        # Get the original request body
        body = await request.body()
        request._body = body  # Save the body for later use
        
        # Try to get the current user
        user_id = None
        try:
            db = SessionLocal()
            user = await get_current_user(request, db)
            user_id = user.id if user else None
        except:
            pass
        finally:
            if 'db' in locals():
                db.close()

        # Process the request and get the response
        response = await call_next(request)
        
        # Only log if the path doesn't start with /docs or /openapi
        if not request.url.path.startswith(('/docs', '/openapi')):
            # Create audit log entry
            try:
                db = SessionLocal()
                
                # Try to parse request body
                try:
                    request_body = json.loads(body)
                except:
                    request_body = None

                # Create audit log
                log_entry = AuditLog(
                    user_id=user_id,
                    action=request.method,
                    resource=request.url.path,
                    access_granted=response.status_code < 400,
                    ip_address=request.client.host,
                    request_method=request.method,
                    request_path=request.url.path,
                    request_body=request_body if request_body else None,
                    response_status=response.status_code,
                    additional_details={
                        "processing_time": (datetime.utcnow() - start_time).total_seconds(),
                        "user_agent": request.headers.get("user-agent"),
                        "query_params": dict(request.query_params)
                    }
                )
                
                db.add(log_entry)
                db.commit()
            except Exception as e:
                print(f"Error creating audit log: {str(e)}")
            finally:
                db.close()

        return response
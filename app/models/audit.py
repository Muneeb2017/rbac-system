from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    action = Column(String, index=True)  # CREATE, READ, UPDATE, DELETE
    resource = Column(String, index=True)  # Which resource was accessed
    resource_id = Column(String, nullable=True)  # ID of the resource if applicable
    access_granted = Column(Boolean)  # Whether access was granted or denied
    ip_address = Column(String, nullable=True)  # Client IP address
    request_method = Column(String)  # HTTP method
    request_path = Column(String)  # API endpoint
    request_body = Column(JSON, nullable=True)  # Request payload
    response_status = Column(Integer)  # HTTP response status
    additional_details = Column(JSON, nullable=True)  # Any additional context

    user = relationship("User", back_populates="audit_logs")
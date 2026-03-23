import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from irp.core.database import Base


class HumanResource(Base):
    __tablename__ = "human_resource"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_id = Column(String, unique=True, nullable=False, index=True)
    type = Column(String, default="human")
    owner = Column(String)
    owner_id = Column(String)

    name = Column(String, nullable=False)

    skills = Column(JSON, default=list)
    availability = Column(Float, default=1.0)
    current_projects = Column(JSON, default=list)
    department = Column(String)
    role = Column(String)

    skill_packages = Column(JSON, default=list)
    capability_level = Column(String)
    api_endpoint = Column(String)
    cost_per_call = Column(Float, default=0)

    preferred_task_types = Column(JSON, default=list)
    excluded_tasks = Column(JSON, default=list)

    status = Column(String, default="available")

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TaskRequest(Base):
    __tablename__ = "task_request"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(String, unique=True, nullable=False, index=True)
    task_type = Column(String, nullable=False)

    features = Column(JSON, default=dict)

    constraints = Column(JSON, default=dict)

    preferences = Column(JSON, default=dict)

    priority = Column(String, default="P2")

    status = Column(String, default="pending")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

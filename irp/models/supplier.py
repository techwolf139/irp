import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from irp.core.database import Base


class SupplierMaster(Base):
    __tablename__ = "supplier_master"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    supplier_id = Column(String, unique=True, nullable=False, index=True)
    source_system = Column(String, nullable=False)
    source_id = Column(String, nullable=False)

    name = Column(String, nullable=False)
    category = Column(String)
    scale = Column(String)

    business_reg_no = Column(String)
    legal_person = Column(String)
    registered_capital = Column(Float)
    risk_score = Column(Float, default=0)
    risk_level = Column(String)
    is_discredited = Column(Boolean, default=False)
    litigation_count = Column(Integer, default=0)
    admin_penalty_count = Column(Integer, default=0)
    operation_status = Column(String)

    rating = Column(Float, default=0)
    cooperation_count = Column(Integer, default=0)

    status = Column(String, default="待审核")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project_links = relationship("ProjectSupplierLink", back_populates="supplier", cascade="all, delete-orphan")


class ProjectSupplierLink(Base):
    __tablename__ = "project_supplier_link"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(String, nullable=False, index=True)
    supplier_id = Column(String, ForeignKey("supplier_master.supplier_id"), nullable=False)
    project_level_rating = Column(Float)
    project_level_tags = Column(JSON, default=list)

    created_at = Column(DateTime, default=datetime.utcnow)

    supplier = relationship("SupplierMaster", back_populates="project_links")

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from irp.core.database import Base


class InventoryView(Base):
    __tablename__ = "inventory_view"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sku_id = Column(String, unique=True, nullable=False, index=True)
    sku_name = Column(String, nullable=False)
    category = Column(String)

    sellable_qty = Column(Integer, default=0)
    reserved_qty = Column(Integer, default=0)
    in_transit_qty = Column(Integer, default=0)
    quality_check_qty = Column(Integer, default=0)
    returned_qty = Column(Integer, default=0)

    available_qty = Column(Integer, default=0)
    total_qty = Column(Integer, default=0)

    reorder_point = Column(Integer, default=0)
    reorder_qty = Column(Integer, default=0)
    lead_time_days = Column(Integer, default=7)

    preferred_supplier_id = Column(String)
    backup_supplier_id = Column(String)

    stock_status = Column(String, default="正常")

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ReplenishmentTask(Base):
    __tablename__ = "replenishment_task"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(String, unique=True, nullable=False, index=True)
    sku_id = Column(String, nullable=False)
    supplier_id = Column(String)
    qty = Column(Integer, nullable=False)
    status = Column(String, default="待采购")
    requisition_id = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)
    estimated_arrival = Column(DateTime)
    completed_at = Column(DateTime)

import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Float, Date, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSON
from irp.core.database import Base


class FundFlow(Base):
    __tablename__ = "fund_flow"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    record_id = Column(String, unique=True, nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    type = Column(String, nullable=False)

    amount = Column(Float, nullable=False)
    currency = Column(String, default="CNY")

    source_system = Column(String, nullable=False)
    source_id = Column(String)

    category = Column(String, index=True)
    sub_category = Column(String)

    project_id = Column(String, index=True)
    supplier_id = Column(String, index=True)
    contract_id = Column(String)

    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class BudgetView(Base):
    __tablename__ = "budget_view"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(String, unique=True, nullable=False, index=True)
    budget_total = Column(Float, default=0)
    budget_spent = Column(Float, default=0)
    budget_committed = Column(Float, default=0)

    categories = Column(JSON, default=dict)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def budget_available(self):
        return self.budget_total - self.budget_spent - self.budget_committed

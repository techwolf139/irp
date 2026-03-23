import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Date, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from irp.core.database import Base


class ContractMaster(Base):
    __tablename__ = "contract_master"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contract_id = Column(String, unique=True, nullable=False, index=True)
    source_system = Column(String, nullable=False)  # SRM/PMS
    source_id = Column(String, nullable=False)

    # 基础
    contract_no = Column(String)  # 合同编号
    title = Column(String, nullable=False)
    type = Column(String)  # 框架协议/执行合同/采购合同/外包合同
    status = Column(String, default="草稿")  # 草稿/生效/履行中/已完成/终止

    # 关联
    supplier_id = Column(String, ForeignKey("supplier_master.supplier_id"))
    project_id = Column(String, index=True)

    # 金额
    total_amount = Column(Float, default=0)
    currency = Column(String, default="CNY")
    tax_rate = Column(Float, default=0.13)

    # 时间
    signed_date = Column(Date)
    start_date = Column(Date)
    end_date = Column(Date)

    # 条款
    payment_terms = Column(Text)
    delivery_terms = Column(Text)
    penalty_clause = Column(Text)
    risk_flags = Column(JSON, default=list)

    # 树状结构
    child_contract_ids = Column(JSON, default=list)  # 子合同ID列表
    parent_contract_id = Column(String, index=True)  # 父合同ID

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PaymentPlan(Base):
    __tablename__ = "payment_plan"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contract_id = Column(String, ForeignKey("contract_master.contract_id"), nullable=False)
    milestone = Column(String, nullable=False)  # 付款节点
    amount = Column(Float, nullable=False)
    due_date = Column(Date)
    status = Column(String, default="待付款")  # 待付款/已付款/逾期
    paid_amount = Column(Float, default=0)
    invoice_ids = Column(JSON, default=list)

    created_at = Column(DateTime, default=datetime.utcnow)

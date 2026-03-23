# IRP 实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 实现 IRP Phase 1，搭建基础设施 + 三大系统集成 + 供应商主数据

**Architecture:** IRP 作为逻辑层，通过 API + Webhook 与 PMS/OMS/SRM 对接

**Tech Stack:** Python (FastAPI), PostgreSQL, Redis, Kafka (可选)

---

## Phase 1: 基础设施

### Task 1: 项目初始化

**Files:**
- Create: `irp/main.py`
- Create: `irp/config.py`
- Create: `irp/__init__.py`
- Create: `requirements.txt`

**Step 1: 创建项目结构**

```bash
mkdir -p irp/{api,core,integrations,models,services,webhooks}
touch irp/__init__.py irp/api/__init__.py irp/core/__init__.py
touch irp/integrations/__init__.py irp/models/__init__.py
touch irp/services/__init__.py irp/webhooks/__init__.py
```

**Step 2: 创建 requirements.txt**

```txt
fastapi==0.109.0
uvicorn==0.27.0
sqlalchemy==2.0.25
asyncpg==0.29.0
redis==5.0.1
pydantic==2.5.3
httpx==0.26.0
python-dotenv==1.0.0
pytest==7.4.4
pytest-asyncio==0.23.3
```

**Step 3: 创建 config.py**

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://localhost:5432/irp"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Integration endpoints
    pms_api_url: str = "http://localhost:8001"
    oms_api_url: str = "http://localhost:8002"
    srm_api_url: str = "http://localhost:8003"
    
    # Sync settings
    sync_interval_seconds: int = 300  # 5 minutes
    
    class Config:
        env_file = ".env"

settings = Settings()
```

**Step 4: Run test to verify**

Run: `python -c "from irp.config import settings; print(settings.database_url)"`
Expected: `postgresql+asyncpg://localhost:5432/irp`

**Step 5: Commit**

```bash
git add irp/ requirements.txt
git commit -m "feat: initialize IRP project structure"
```

---

### Task 2: 数据库模型 - 供应商主数据

**Files:**
- Create: `irp/models/supplier.py`
- Create: `tests/models/test_supplier.py`

**Step 1: 创建 SupplierMaster 模型**

```python
from sqlalchemy import Column, String, Float, Boolean, Integer, DateTime, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

class SupplierMaster(Base):
    __tablename__ = "supplier_master"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    supplier_id = Column(String, unique=True, nullable=False, index=True)
    source_system = Column(String, nullable=False)  # SRM/PMS
    source_id = Column(String, nullable=False)
    
    # 基础信息
    name = Column(String, nullable=False)
    category = Column(String)  # 制造商/贸易商/服务商
    scale = Column(String)  # 大型/中型/小型
    
    # SRM主数据
    business_reg_no = Column(String)
    legal_person = Column(String)
    registered_capital = Column(Float)
    risk_score = Column(Float, default=0)  # 0-100
    risk_level = Column(String)  # 高/中/低
    is_discredited = Column(Boolean, default=False)
    litigation_count = Column(Integer, default=0)
    admin_penalty_count = Column(Integer, default=0)
    operation_status = Column(String)  # 正常/异常/吊销
    
    # 评估
    rating = Column(Float, default=0)  # 0-5
    cooperation_count = Column(Integer, default=0)
    
    # 状态
    status = Column(String, default="待审核")  # 待审核/合格/黑名单
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ProjectSupplierLink(Base):
    __tablename__ = "project_supplier_link"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(String, nullable=False, index=True)
    supplier_id = Column(String, ForeignKey("supplier_master.supplier_id"), nullable=False)
    project_level_rating = Column(Float)
    project_level_tags = Column(JSON, default=list)
    
    created_at = Column(DateTime, default=datetime.utcnow)
```

**Step 2: 创建测试**

```python
import pytest
from irp.models.supplier import SupplierMaster, ProjectSupplierLink

def test_supplier_master_creation():
    supplier = SupplierMaster(
        supplier_id="SUP001",
        source_system="SRM",
        source_id="SRM001",
        name="测试供应商",
        category="制造商",
        risk_score=25.0,
        risk_level="低",
        status="合格"
    )
    assert supplier.supplier_id == "SUP001"
    assert supplier.risk_level == "低"
    assert supplier.status == "合格"

def test_project_supplier_link():
    link = ProjectSupplierLink(
        project_id="PRJ001",
        supplier_id="SUP001",
        project_level_rating=4.5
    )
    assert link.project_id == "PRJ001"
    assert link.project_level_rating == 4.5
```

**Step 3: Run test to verify**

Run: `pytest tests/models/test_supplier.py -v`
Expected: 2 passed

**Step 4: Run linter**

Run: `python -m py_compile irp/models/supplier.py`
Expected: No output (success)

**Step 5: Commit**

```bash
git add irp/models/supplier.py tests/models/test_supplier.py
git commit -m "feat: add SupplierMaster model for supplier master data"
```

---

### Task 3: 基础 API 框架

**Files:**
- Create: `irp/api/main.py`
- Create: `irp/api/suppliers.py`
- Create: `tests/api/test_suppliers.py`

**Step 1: 创建 FastAPI 应用**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="IRP API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Import routers
from irp.api.suppliers import router as suppliers_router
app.include_router(suppliers_router, prefix="/api/v1", tags=["suppliers"])
```

**Step 2: 创建供应商路由**

```python
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from irp.core.database import get_db
from irp.models.supplier import SupplierMaster
from pydantic import BaseModel

router = APIRouter()

class SupplierResponse(BaseModel):
    supplier_id: str
    name: str
    risk_level: str
    rating: float
    status: str
    
    class Config:
        from_attributes = True

@router.get("/suppliers", response_model=List[SupplierResponse])
async def list_suppliers(
    risk_level: str = None,
    status: str = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(SupplierMaster)
    if risk_level:
        query = query.where(SupplierMaster.risk_level == risk_level)
    if status:
        query = query.where(SupplierMaster.status == status)
    
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/suppliers/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(supplier_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(SupplierMaster).where(SupplierMaster.supplier_id == supplier_id)
    )
    supplier = result.scalar_one_or_none()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier
```

**Step 3: Run test to verify**

Run: `pytest tests/api/test_suppliers.py -v`
Expected: API tests pass

**Step 4: Run linter**

Run: `python -m py_compile irp/api/main.py irp/api/suppliers.py`
Expected: No output

**Step 5: Commit**

```bash
git add irp/api/main.py irp/api/suppliers.py tests/api/test_suppliers.py
git commit -m "feat: add FastAPI framework and supplier API endpoints"
```

---

## Phase 2: 系统集成

### Task 4: PMS 集成

**Files:**
- Create: `irp/integrations/pms_client.py`
- Create: `tests/integrations/test_pms_client.py`

**Step 1: 创建 PMS 客户端**

```python
import httpx
from typing import List, Optional
from pydantic import BaseModel
from datetime import date

class PMSProject(BaseModel):
    project_id: str
    name: str
    status: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class PMSPerson(BaseModel):
    person_id: str
    name: str
    skills: List[str] = []
    department: str
    availability: float = 1.0

class PMSClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_projects(self) -> List[PMSProject]:
        response = await self.client.get(f"{self.base_url}/api/projects")
        response.raise_for_status()
        return [PMSProject(**p) for p in response.json()]
    
    async def get_persons(self) -> List[PMSPerson]:
        response = await self.client.get(f"{self.base_url}/api/persons")
        response.raise_for_status()
        return [PMSPerson(**p) for p in response.json()]
    
    async def close(self):
        await self.client.aclose()
```

**Step 2: 创建测试**

```python
import pytest
from unittest.mock import AsyncMock, patch
from irp.integrations.pms_client import PMSClient, PMSProject

@pytest.mark.asyncio
async def test_get_projects():
    with patch('httpx.AsyncClient') as mock_client:
        mock_instance = AsyncMock()
        mock_instance.get.return_value.json.return_value = [
            {"project_id": "PRJ001", "name": "项目A", "status": "进行中"}
        ]
        mock_client.return_value.__aenter__.return_value = mock_instance
        
        client = PMSClient("http://localhost:8001")
        projects = await client.get_projects()
        
        assert len(projects) == 1
        assert projects[0].project_id == "PRJ001"
```

**Step 3: Run test**

Run: `pytest tests/integrations/test_pms_client.py -v`
Expected: 1 passed

**Step 4: Commit**

```bash
git add irp/integrations/pms_client.py tests/integrations/test_pms_client.py
git commit -m "feat: add PMS integration client"
```

---

### Task 5: OMS 集成

**Files:**
- Create: `irp/integrations/oms_client.py`
- Create: `tests/integrations/test_oms_client.py`

**Step 1: 创建 OMS 客户端**

```python
import httpx
from typing import List, Optional
from pydantic import BaseModel

class OMSInventory(BaseModel):
    sku_id: str
    sku_name: str
    sellable_qty: int
    reserved_qty: int
    in_transit_qty: int = 0
    available_qty: int  # computed: sellable - reserved

class OMSClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_inventory(self, sku_id: str) -> Optional[OMSInventory]:
        response = await self.client.get(f"{self.base_url}/api/inventory/{sku_id}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        data = response.json()
        data['available_qty'] = data['sellable_qty'] - data['reserved_qty']
        return OMSInventory(**data)
    
    async def list_inventory(self, stock_status: str = None) -> List[OMSInventory]:
        params = {}
        if stock_status:
            params['stock_status'] = stock_status
        response = await self.client.get(f"{self.base_url}/api/inventory", params=params)
        response.raise_for_status()
        items = response.json()
        for item in items:
            item['available_qty'] = item['sellable_qty'] - item['reserved_qty']
        return [OMSInventory(**i) for i in items]
    
    async def close(self):
        await self.client.aclose()
```

**Step 2: 创建测试**

```python
import pytest
from unittest.mock import AsyncMock, patch
from irp.integrations.oms_client import OMSClient, OMSInventory

@pytest.mark.asyncio
async def test_get_inventory():
    with patch('httpx.AsyncClient') as mock_client:
        mock_instance = AsyncMock()
        mock_instance.get.return_value.json.return_value = {
            "sku_id": "SKU001",
            "sku_name": "产品A",
            "sellable_qty": 100,
            "reserved_qty": 20,
            "in_transit_qty": 50
        }
        mock_client.return_value.__aenter__.return_value = mock_instance
        
        client = OMSClient("http://localhost:8002")
        inventory = await client.get_inventory("SKU001")
        
        assert inventory.sku_id == "SKU001"
        assert inventory.available_qty == 80  # 100 - 20
```

**Step 3: Run test**

Run: `pytest tests/integrations/test_oms_client.py -v`
Expected: 1 passed

**Step 4: Commit**

```bash
git add irp/integrations/oms_client.py tests/integrations/test_oms_client.py
git commit -m "feat: add OMS integration client"
```

---

### Task 6: SRM 集成

**Files:**
- Create: `irp/integrations/srm_client.py`
- Create: `tests/integrations/test_srm_client.py`

**Step 1: 创建 SRM 客户端**

```python
import httpx
from typing import List, Optional
from pydantic import BaseModel

class SRMSupplier(BaseModel):
    supplier_id: str
    name: str
    business_reg_no: Optional[str] = None
    risk_score: float = 0
    risk_level: str = "中"
    is_discredited: bool = False
    rating: float = 0
    status: str = "待审核"

class SRMPurchaseOrder(BaseModel):
    po_id: str
    supplier_id: str
    status: str
    items: List[dict] = []

class SRMClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_suppliers(self, risk_level: str = None) -> List[SRMSupplier]:
        params = {}
        if risk_level:
            params['risk_level'] = risk_level
        response = await self.client.get(f"{self.base_url}/api/suppliers", params=params)
        response.raise_for_status()
        return [SRMSupplier(**s) for s in response.json()]
    
    async def create_purchase_requisition(self, items: List[dict]) -> str:
        response = await self.client.post(
            f"{self.base_url}/api/purchase-requisitions",
            json={"items": items}
        )
        response.raise_for_status()
        return response.json()["requisition_id"]
    
    async def get_purchase_orders(self, supplier_id: str = None) -> List[SRMPurchaseOrder]:
        params = {}
        if supplier_id:
            params['supplier_id'] = supplier_id
        response = await self.client.get(f"{self.base_url}/api/purchase-orders", params=params)
        response.raise_for_status()
        return [SRMPurchaseOrder(**po) for po in response.json()]
    
    async def close(self):
        await self.client.aclose()
```

**Step 2: 创建测试**

```python
import pytest
from unittest.mock import AsyncMock, patch
from irp.integrations.srm_client import SRMClient, SRMSupplier

@pytest.mark.asyncio
async def test_get_suppliers():
    with patch('httpx.AsyncClient') as mock_client:
        mock_instance = AsyncMock()
        mock_instance.get.return_value.json.return_value = [
            {
                "supplier_id": "SUP001",
                "name": "测试供应商",
                "risk_score": 25.0,
                "risk_level": "低",
                "is_discredited": False,
                "rating": 4.5
            }
        ]
        mock_client.return_value.__aenter__.return_value = mock_instance
        
        client = SRMClient("http://localhost:8003")
        suppliers = await client.get_suppliers(risk_level="低")
        
        assert len(suppliers) == 1
        assert suppliers[0].risk_level == "低"
```

**Step 3: Run test**

Run: `pytest tests/integrations/test_srm_client.py -v`
Expected: 1 passed

**Step 4: Commit**

```bash
git add irp/integrations/srm_client.py tests/integrations/test_srm_client.py
git commit -m "feat: add SRM integration client"
```

---

## Phase 3: 供应商主数据

### Task 7: 供应商映射服务

**Files:**
- Create: `irp/services/supplier_mapping_service.py`
- Create: `tests/services/test_supplier_mapping_service.py`

**Step 1: 创建供应商映射服务**

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from irp.models.supplier import SupplierMaster, ProjectSupplierLink

class SupplierMappingService:
    """供应商映射服务 - 管理 PMS 项目供应商 ↔ SRM 企业供应商的映射"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_link(self, project_id: str, supplier_id: str, 
                         rating: float = None, tags: list = None) -> ProjectSupplierLink:
        """创建项目与供应商的关联"""
        link = ProjectSupplierLink(
            project_id=project_id,
            supplier_id=supplier_id,
            project_level_rating=rating,
            project_level_tags=tags or []
        )
        self.db.add(link)
        await self.db.commit()
        await self.db.refresh(link)
        return link
    
    async def get_project_suppliers(self, project_id: str) -> list:
        """获取项目关联的所有供应商"""
        result = await self.db.execute(
            select(ProjectSupplierLink, SupplierMaster)
            .join(SupplierMaster, ProjectSupplierLink.supplier_id == SupplierMaster.supplier_id)
            .where(ProjectSupplierLink.project_id == project_id)
        )
        return result.all()
    
    async def get_supplier_projects(self, supplier_id: str) -> list:
        """获取供应商关联的所有项目"""
        result = await self.db.execute(
            select(ProjectSupplierLink)
            .where(ProjectSupplierLink.supplier_id == supplier_id)
        )
        return result.scalars().all()
```

**Step 2: 创建测试**

```python
import pytest
from unittest.mock import AsyncMock
from irp.services.supplier_mapping_service import SupplierMappingService

@pytest.mark.asyncio
async def test_create_link():
    mock_db = AsyncMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    
    service = SupplierMappingService(mock_db)
    link = await service.create_link(
        project_id="PRJ001",
        supplier_id="SUP001",
        rating=4.5,
        tags=["IT", "外包"]
    )
    
    assert link.project_id == "PRJ001"
    assert link.supplier_id == "SUP001"
    mock_db.add.assert_called_once()
```

**Step 3: Run test**

Run: `pytest tests/services/test_supplier_mapping_service.py -v`
Expected: 1 passed

**Step 4: Commit**

```bash
git add irp/services/supplier_mapping_service.py tests/services/test_supplier_mapping_service.py
git commit -m "feat: add supplier mapping service for project-supplier linking"
```

---

### Task 8: 供应商同步服务

**Files:**
- Create: `irp/services/supplier_sync_service.py`
- Create: `tests/services/test_supplier_sync_service.py`

**Step 1: 创建供应商同步服务**

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from irp.models.supplier import SupplierMaster
from irp.integrations.srm_client import SRMClient
from irp.integrations.pms_client import PMSClient

class SupplierSyncService:
    """供应商同步服务 - 从 SRM/PMS 同步供应商数据到 IRP"""
    
    def __init__(self, db: AsyncSession, srm_client: SRMClient, pms_client: PMSClient):
        self.db = db
        self.srm = srm_client
        self.pms = pms_client
    
    async def sync_from_srm(self):
        """从 SRM 同步供应商主数据"""
        srm_suppliers = await self.srm.get_suppliers()
        
        for srm_sup in srm_suppliers:
            # 检查是否已存在
            result = await self.db.execute(
                select(SupplierMaster).where(
                    SupplierMaster.source_system == "SRM",
                    SupplierMaster.source_id == srm_sup.supplier_id
                )
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                # 更新
                existing.name = srm_sup.name
                existing.risk_score = srm_sup.risk_score
                existing.risk_level = srm_sup.risk_level
                existing.is_discredited = srm_sup.is_discredited
                existing.rating = srm_sup.rating
                existing.status = srm_sup.status
            else:
                # 创建
                supplier = SupplierMaster(
                    supplier_id=f"SRM-{srm_sup.supplier_id}",
                    source_system="SRM",
                    source_id=srm_sup.supplier_id,
                    name=srm_sup.name,
                    business_reg_no=srm_sup.business_reg_no,
                    risk_score=srm_sup.risk_score,
                    risk_level=srm_sup.risk_level,
                    is_discredited=srm_sup.is_discredited,
                    rating=srm_sup.rating,
                    status=srm_sup.status
                )
                self.db.add(supplier)
        
        await self.db.commit()
    
    async def get_supplier_stats(self) -> dict:
        """获取供应商统计"""
        total = await self.db.execute(select(SupplierMaster))
        total_count = len(total.scalars().all())
        
        low_risk = await self.db.execute(
            select(SupplierMaster).where(SupplierMaster.risk_level == "低")
        )
        low_risk_count = len(low_risk.scalars().all())
        
        return {
            "total": total_count,
            "low_risk": low_risk_count,
            "medium_risk": total_count - low_risk_count
        }
```

**Step 2: 创建测试**

```python
import pytest
from unittest.mock import AsyncMock, patch
from irp.services.supplier_sync_service import SupplierSyncService

@pytest.mark.asyncio
async def test_sync_from_srm():
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock()
    mock_db.commit = AsyncMock()
    
    mock_srm = AsyncMock()
    mock_srm.get_suppliers.return_value = [
        type('Obj', (), {
            'supplier_id': 'SUP001',
            'name': '测试供应商',
            'business_reg_no': '91110000xxxx',
            'risk_score': 25.0,
            'risk_level': '低',
            'is_discredited': False,
            'rating': 4.5,
            'status': '合格'
        })()
    ]
    
    mock_pms = AsyncMock()
    
    service = SupplierSyncService(mock_db, mock_srm, mock_pms)
    await service.sync_from_srm()
    
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
```

**Step 3: Run test**

Run: `pytest tests/services/test_supplier_sync_service.py -v`
Expected: 1 passed

**Step 4: Commit**

```bash
git add irp/services/supplier_sync_service.py tests/services/test_supplier_sync_service.py
git commit -m "feat: add supplier sync service from SRM"
```

---

### Task 9: Webhook 处理 - 供应商变更

**Files:**
- Create: `irp/webhooks/handlers.py`
- Create: `tests/webhooks/test_handlers.py`

**Step 1: 创建 Webhook 处理器**

```python
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Optional
from irp.services.supplier_sync_service import SupplierSyncService

router = APIRouter()

class SupplierRiskChangedPayload(BaseModel):
    supplier_id: str
    old_score: float
    new_score: float
    risk_level_changed: bool
    new_risk_level: Optional[str] = None

@router.post("/webhook/supplier-risk-changed")
async def handle_supplier_risk_changed(
    payload: SupplierRiskChangedPayload,
    request: Request
):
    """处理 SRM 供应商风险评分变更"""
    # 获取服务实例 (通过 app state)
    service: SupplierSyncService = request.app.state.supplier_sync_service
    
    # 更新供应商风险数据
    # 这里可以添加通知逻辑
    print(f"供应商 {payload.supplier_id} 风险评分变更: {payload.old_score} -> {payload.new_score}")
    
    # 如果风险等级变化，触发预警
    if payload.risk_level_changed and payload.new_risk_level == "高":
        await send_high_risk_alert(payload.supplier_id, payload.new_score)
    
    return {"status": "received"}

async def send_high_risk_alert(supplier_id: str, risk_score: float):
    """发送高风险预警"""
    # TODO: 实现 IM/邮件通知
    pass
```

**Step 2: 创建测试**

```python
import pytest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
from irp.webhooks.handlers import handle_supplier_risk_changed, SupplierRiskChangedPayload

def test_supplier_risk_changed_webhook():
    payload = SupplierRiskChangedPayload(
        supplier_id="SUP001",
        old_score=25.0,
        new_score=75.0,
        risk_level_changed=True,
        new_risk_level="高"
    )
    
    # Mock request with app state
    mock_request = AsyncMock()
    mock_request.app.state.supplier_sync_service = AsyncMock()
    
    # 直接测试 handler
    response = handle_supplier_risk_changed(payload, mock_request)
    
    assert response == {"status": "received"}
```

**Step 3: Run test**

Run: `pytest tests/webhooks/test_handlers.py -v`
Expected: 1 passed

**Step 4: Commit**

```bash
git add irp/webhooks/handlers.py tests/webhooks/test_handlers.py
git commit -m "feat: add webhook handler for supplier risk changes"
```

---

## Phase 4: 供应商 API 增强

### Task 10: 供应商查询 API

**Files:**
- Modify: `irp/api/suppliers.py`
- Create: `tests/api/test_suppliers_enhanced.py`

**Step 1: 增强供应商 API**

```python
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from irp.core.database import get_db
from irp.models.supplier import SupplierMaster, ProjectSupplierLink
from pydantic import BaseModel

router = APIRouter()

# ... existing code ...

@router.get("/suppliers/stats")
async def get_supplier_stats(db: AsyncSession = Depends(get_db)):
    """获取供应商统计"""
    total = await db.execute(select(func.count(SupplierMaster.id)))
    total_count = total.scalar()
    
    low_risk = await db.execute(
        select(func.count(SupplierMaster.id))
        .where(SupplierMaster.risk_level == "低")
    )
    low_risk_count = low_risk.scalar()
    
    return {
        "total": total_count,
        "low_risk": low_risk_count,
        "medium_risk": total_count - low_risk_count
    }

@router.get("/suppliers/{supplier_id}/projects")
async def get_supplier_projects(
    supplier_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取供应商关联的项目"""
    result = await db.execute(
        select(ProjectSupplierLink)
        .where(ProjectSupplierLink.supplier_id == supplier_id)
    )
    links = result.scalars().all()
    return [
        {
            "project_id": link.project_id,
            "project_level_rating": link.project_level_rating,
            "project_level_tags": link.project_level_tags
        }
        for link in links
    ]
```

**Step 2: Run linter**

Run: `python -m py_compile irp/api/suppliers.py`
Expected: No output

**Step 3: Commit**

```bash
git add irp/api/suppliers.py
git commit -m "feat: add supplier stats and project linking API"
```

---

## Phase 5: 定时同步

### Task 11: 定时同步任务

**Files:**
- Create: `irp/services/scheduler.py`
- Create: `tests/services/test_scheduler.py`

**Step 1: 创建定时同步服务**

```python
import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from irp.services.supplier_sync_service import SupplierSyncService

class IRPScheduler:
    """IRP 定时任务调度器"""
    
    def __init__(self, sync_service: SupplierSyncService):
        self.scheduler = AsyncIOScheduler()
        self.sync_service = sync_service
    
    def start(self):
        """启动调度器"""
        # 每5分钟同步供应商数据
        self.scheduler.add_job(
            self.sync_suppliers,
            trigger=IntervalTrigger(minutes=5),
            id="sync_suppliers",
            replace_existing=True
        )
        
        self.scheduler.start()
    
    async def sync_suppliers(self):
        """同步供应商数据"""
        print(f"[{datetime.now()}] 开始同步供应商数据...")
        try:
            await self.sync_service.sync_from_srm()
            print(f"[{datetime.now()}] 供应商同步完成")
        except Exception as e:
            print(f"[{datetime.now()}] 供应商同步失败: {e}")
    
    def stop(self):
        """停止调度器"""
        self.scheduler.shutdown()
```

**Step 2: 创建测试**

```python
import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler

def test_scheduler_creation():
    mock_service = AsyncMock()
    scheduler = AsyncIOScheduler()
    
    # 不实际启动，只测试添加任务
    scheduler.add_job(
        mock_service.sync_from_srm,
        trigger=IntervalTrigger(minutes=5),
        id="sync_suppliers_test"
    )
    
    assert len(scheduler.get_jobs()) == 1
    scheduler.shutdown()
```

**Step 3: Commit**

```bash
git add irp/services/scheduler.py tests/services/test_scheduler.py
git commit -m "feat: add scheduler for periodic supplier sync"
```

---

## Phase 6: 集成测试

### Task 12: 端到端集成测试

**Files:**
- Create: `tests/e2e/test_integration.py`

**Step 1: 创建集成测试**

```python
import pytest
from httpx import AsyncClient
from irp.api.main import app

@pytest.mark.asyncio
async def test_full_supplier_flow():
    """测试完整的供应商流程"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 1. 创建供应商 (模拟 SRM 同步)
        # 2. 查询供应商列表
        response = await client.get("/api/v1/suppliers")
        assert response.status_code == 200
        
        # 3. 获取统计
        response = await client.get("/api/v1/suppliers/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "low_risk" in data

@pytest.mark.asyncio
async def test_webhook_endpoint():
    """测试 Webhook 端点"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/webhooks/supplier-risk-changed",
            json={
                "supplier_id": "SUP001",
                "old_score": 25.0,
                "new_score": 75.0,
                "risk_level_changed": True,
                "new_risk_level": "高"
            }
        )
        assert response.status_code == 200
```

**Step 2: Run integration test**

Run: `pytest tests/e2e/test_integration.py -v`
Expected: All tests pass

**Step 3: Commit**

```bash
git add tests/e2e/test_integration.py
git commit -m "test: add e2e integration tests"
```

---

## Phase 7: 文档与部署

### Task 13: API 文档

**Files:**
- Create: `docs/API.md`

**Step 1: 编写 API 文档**

```markdown
# IRP API 文档

## 供应商 API

### 获取供应商列表
```
GET /api/v1/suppliers?risk_level=低&status=合格
```

### 获取供应商详情
```
GET /api/v1/suppliers/{supplier_id}
```

### 获取供应商统计
```
GET /api/v1/suppliers/stats
```

### 获取供应商关联项目
```
GET /api/v1/suppliers/{supplier_id}/projects
```

## Webhook

### 供应商风险变更
```
POST /api/v1/webhooks/supplier-risk-changed

{
  "supplier_id": "SUP001",
  "old_score": 25.0,
  "new_score": 75.0,
  "risk_level_changed": true,
  "new_risk_level": "高"
}
```
```

**Step 2: Commit**

```bash
git add docs/API.md
git commit -m "docs: add API documentation"
```

---

## 总结

**Phase 1 完成后的能力**:
- IRP 基础架构 (FastAPI + SQLAlchemy)
- PMS/OMS/SRM 三个集成客户端
- 供应商主数据模型
- 供应商同步服务 (SRM → IRP)
- Webhook 处理 (供应商风险变更)
- 定时同步任务
- 基础 API 端点

**下一步 (Phase 2-4)**:
- 合同中心
- 库存视图 + 触发补货
- 人力池 + AI技能
- 规则引擎
- 任务调度
- 完整 Web 控制台

---

## Phase 2: 合同中心

### Task 14: 合同数据模型

**Files:**
- Create: `irp/models/contract.py`
- Create: `tests/models/test_contract.py`

**Step 1: 创建合同模型**

```python
from sqlalchemy import Column, String, Float, Date, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSON
from datetime import datetime
import uuid

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
```

**Step 2: 创建测试**

```python
def test_contract_master_creation():
    contract = ContractMaster(
        contract_id="CON001",
        source_system="SRM",
        source_id="SRM-CON001",
        title="框架采购协议",
        type="框架协议",
        total_amount=1000000.0,
        status="生效"
    )
    assert contract.contract_id == "CON001"
    assert contract.type == "框架协议"

def test_payment_plan():
    plan = PaymentPlan(
        contract_id="CON001",
        milestone="首付款",
        amount=300000.0,
        due_date=date(2024, 6, 1),
        status="待付款"
    )
    assert plan.milestone == "首付款"
    assert plan.amount == 300000.0
```

**Step 3: Run test**

Run: `pytest tests/models/test_contract.py -v`
Expected: 2 passed

**Step 4: Commit**

```bash
git add irp/models/contract.py tests/models/test_contract.py
git commit -m "feat: add ContractMaster and PaymentPlan models"
```

---

### Task 15: 合同同步服务

**Files:**
- Create: `irp/services/contract_sync_service.py`
- Create: `tests/services/test_contract_sync_service.py`

**Step 1: 创建合同同步服务**

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from irp.models.contract import ContractMaster, PaymentPlan
from irp.integrations.srm_client import SRMClient
from irp.integrations.pms_client import PMSClient

class ContractSyncService:
    """合同同步服务 - 从 SRM/PMS 同步合同数据到 IRP"""
    
    def __init__(self, db: AsyncSession, srm_client: SRMClient, pms_client: PMSClient):
        self.db = db
        self.srm = srm_client
        self.pms = pms_client
    
    async def sync_from_srm(self):
        """从 SRM 同步合同主数据"""
        srm_contracts = await self.srm.get_contracts()
        
        for srm_con in srm_contracts:
            result = await self.db.execute(
                select(ContractMaster).where(
                    ContractMaster.source_system == "SRM",
                    ContractMaster.source_id == srm_con.contract_id
                )
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                existing.title = srm_con.title
                existing.status = srm_con.status
                existing.total_amount = srm_con.total_amount
            else:
                contract = ContractMaster(
                    contract_id=f"SRM-{srm_con.contract_id}",
                    source_system="SRM",
                    source_id=srm_con.contract_id,
                    title=srm_con.title,
                    type=srm_con.type,
                    status=srm_con.status,
                    supplier_id=srm_con.supplier_id,
                    total_amount=srm_con.total_amount
                )
                self.db.add(contract)
        
        await self.db.commit()
    
    async def link_pms_contract(self, srm_contract_id: str, pms_contract_id: str):
        """将 PMS 合同关联到 SRM 主合同下"""
        result = await self.db.execute(
            select(ContractMaster).where(ContractMaster.contract_id == srm_contract_id)
        )
        parent = result.scalar_one_or_none()
        
        if parent:
            child = ContractMaster(
                contract_id=f"PMS-{pms_contract_id}",
                source_system="PMS",
                source_id=pms_contract_id,
                title=f"项目合同 - {pms_contract_id}",
                type="执行合同",
                parent_contract_id=srm_contract_id,
                supplier_id=parent.supplier_id
            )
            self.db.add(child)
            
            # 更新父合同的 child_contract_ids
            if parent.child_contract_ids is None:
                parent.child_contract_ids = []
            parent.child_contract_ids.append(child.contract_id)
            
            await self.db.commit()
```

**Step 2: 创建测试**

```python
@pytest.mark.asyncio
async def test_link_pms_contract():
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock()
    mock_db.commit = AsyncMock()
    
    mock_srm = AsyncMock()
    mock_pms = AsyncMock()
    
    service = ContractSyncService(mock_db, mock_srm, mock_pms)
    
    # Mock parent contract
    mock_parent = MagicMock()
    mock_parent.child_contract_ids = []
    mock_db.execute.return_value.scalar_one_or_none.return_value = mock_parent
    
    await service.link_pms_contract("SRM-CON001", "PMS-CON001")
    
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
```

**Step 3: Run test**

Run: `pytest tests/services/test_contract_sync_service.py -v`
Expected: 1 passed

**Step 4: Commit**

```bash
git add irp/services/contract_sync_service.py tests/services/test_contract_sync_service.py
git commit -m "feat: add contract sync service"
```

---

### Task 16: 合同审批流

**Files:**
- Create: `irp/services/contract_approval_service.py`
- Create: `tests/services/test_contract_approval_service.py`

**Step 1: 创建合同审批服务**

```python
from enum import Enum
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ContractType(str, Enum):
    PURCHASE = "采购合同"
    OUTSOURCE = "外包合同"
    FRAMEWORK = "框架协议"

class ApprovalStep(BaseModel):
    step_name: str
    approver_role: str
    status: str = "pending"  # pending/approved/rejected
    approver_id: Optional[str] = None
    comment: Optional[str] = None
    approved_at: Optional[datetime] = None

class ContractApprovalFlow:
    """合同审批流程"""
    
    FLOW_MAP = {
        ContractType.PURCHASE: [
            ApprovalStep(step_name="创建", approver_role="采购员"),
            ApprovalStep(step_name="采购负责人审批", approver_role="采购负责人"),
            ApprovalStep(step_name="法务审批", approver_role="法务"),
            ApprovalStep(step_name="财务审批", approver_role="财务"),
        ],
        ContractType.OUTSOURCE: [
            ApprovalStep(step_name="创建", approver_role="采购员"),
            ApprovalStep(step_name="项目负责人审批", approver_role="项目负责人"),
            ApprovalStep(step_name="法务审批", approver_role="法务"),
        ],
        ContractType.FRAMEWORK: [
            ApprovalStep(step_name="创建", approver_role="采购员"),
            ApprovalStep(step_name="法务审批", approver_role="法务"),
        ],
    }
    
    @classmethod
    def get_flow(cls, contract_type: ContractType) -> List[ApprovalStep]:
        return cls.FLOW_MAP.get(contract_type, cls.FLOW_MAP[ContractType.FRAMEWORK])
    
    @classmethod
    def create_approval_record(cls, contract_id: str, contract_type: ContractType) -> dict:
        flow = cls.get_flow(contract_type)
        return {
            "contract_id": contract_id,
            "current_step": 0,
            "steps": [step.model_dump() for step in flow],
            "status": "pending"  # pending/approved/rejected/completed
        }
```

**Step 2: 创建测试**

```python
def test_contract_approval_flow_purchase():
    flow = ContractApprovalFlow.get_flow(ContractType.PURCHASE)
    assert len(flow) == 4
    assert flow[0].step_name == "创建"
    assert flow[1].step_name == "采购负责人审批"

def test_contract_approval_flow_outsource():
    flow = ContractApprovalFlow.get_flow(ContractType.OUTSOURCE)
    assert len(flow) == 3
    assert flow[1].step_name == "项目负责人审批"

def test_create_approval_record():
    record = ContractApprovalFlow.create_approval_record("CON001", ContractType.PURCHASE)
    assert record["contract_id"] == "CON001"
    assert record["current_step"] == 0
    assert len(record["steps"]) == 4
    assert record["status"] == "pending"
```

**Step 3: Run test**

Run: `pytest tests/services/test_contract_approval_service.py -v`
Expected: 3 passed

**Step 4: Commit**

```bash
git add irp/services/contract_approval_service.py tests/services/test_contract_approval_service.py
git commit -m "feat: add contract approval workflow service"
```

---

## Phase 3: 库存视图 + 触发补货

### Task 17: 库存视图模型

**Files:**
- Create: `irp/models/inventory.py`
- Create: `tests/models/test_inventory.py`

**Step 1: 创建库存视图模型**

```python
from sqlalchemy import Column, String, Integer, DateTime, Float
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

class InventoryView(Base):
    __tablename__ = "inventory_view"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sku_id = Column(String, unique=True, nullable=False, index=True)
    sku_name = Column(String, nullable=False)
    category = Column(String)
    
    # 库存状态
    sellable_qty = Column(Integer, default=0)
    reserved_qty = Column(Integer, default=0)
    in_transit_qty = Column(Integer, default=0)  # SRM采购在途
    quality_check_qty = Column(Integer, default=0)
    returned_qty = Column(Integer, default=0)
    
    # 计算字段 (数据库中冗余存储，用于快速查询)
    available_qty = Column(Integer, default=0)  # sellable - reserved
    total_qty = Column(Integer, default=0)
    
    # 补货配置
    reorder_point = Column(Integer, default=0)
    reorder_qty = Column(Integer, default=0)
    lead_time_days = Column(Integer, default=7)
    
    # 供应商
    preferred_supplier_id = Column(String)
    backup_supplier_id = Column(String)
    
    # 状态
    stock_status = Column(String, default="正常")  # 正常/预警/缺货/超库存
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ReplenishmentTask(Base):
    __tablename__ = "replenishment_task"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(String, unique=True, nullable=False, index=True)
    sku_id = Column(String, nullable=False)
    supplier_id = Column(String)
    qty = Column(Integer, nullable=False)
    status = Column(String, default="待采购")  # 待采购/采购中/已到库/已取消
    requisition_id = Column(String)  # SRM采购申请ID
    
    created_at = Column(DateTime, default=datetime.utcnow)
    estimated_arrival = Column(DateTime)
    completed_at = Column(DateTime)
```

**Step 2: 创建测试**

```python
def test_inventory_view_creation():
    inventory = InventoryView(
        sku_id="SKU001",
        sku_name="产品A",
        sellable_qty=100,
        reserved_qty=20,
        in_transit_qty=50,
        available_qty=80,  # 100 - 20
        stock_status="正常"
    )
    assert inventory.available_qty == 80
    assert inventory.total_qty == 170  # 100 + 50

def test_replenishment_task_creation():
    task = ReplenishmentTask(
        task_id="RPT001",
        sku_id="SKU001",
        supplier_id="SUP001",
        qty=100,
        status="待采购"
    )
    assert task.status == "待采购"
```

**Step 3: Run test**

Run: `pytest tests/models/test_inventory.py -v`
Expected: 2 passed

**Step 4: Commit**

```bash
git add irp/models/inventory.py tests/models/test_inventory.py
git commit -m "feat: add InventoryView and ReplenishmentTask models"
```

---

### Task 18: 库存同步服务

**Files:**
- Create: `irp/services/inventory_sync_service.py`
- Create: `tests/services/test_inventory_sync_service.py`

**Step 1: 创建库存同步服务**

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from irp.models.inventory import InventoryView, ReplenishmentTask
from irp.integrations.oms_client import OMSClient
from irp.integrations.srm_client import SRMClient

class InventorySyncService:
    """库存同步服务 - 从 OMS/SRM 同步库存数据"""
    
    def __init__(self, db: AsyncSession, oms_client: OMSClient, srm_client: SRMClient):
        self.db = db
        self.oms = oms_client
        self.srm = srm_client
    
    async def sync_from_oms(self):
        """从 OMS 同步库存数据"""
        oms_inventory_list = await self.oms.list_inventory()
        
        for oms_inv in oms_inventory_list:
            result = await self.db.execute(
                select(InventoryView).where(InventoryView.sku_id == oms_inv.sku_id)
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                existing.sellable_qty = oms_inv.sellable_qty
                existing.reserved_qty = oms_inv.reserved_qty
                existing.available_qty = oms_inv.available_qty
            else:
                inventory = InventoryView(
                    sku_id=oms_inv.sku_id,
                    sku_name=oms_inv.sku_name,
                    sellable_qty=oms_inv.sellable_qty,
                    reserved_qty=oms_inv.reserved_qty,
                    available_qty=oms_inv.available_qty
                )
                self.db.add(inventory)
        
        await self.db.commit()
    
    async def sync_in_transit_from_srm(self):
        """从 SRM 同步采购在途数量"""
        # 获取所有进行中的采购订单
        purchase_orders = await self.srm.get_purchase_orders(status="采购中")
        
        for po in purchase_orders:
            for item in po.items:
                result = await self.db.execute(
                    select(InventoryView).where(InventoryView.sku_id == item["sku_id"])
                )
                inventory = result.scalar_one_or_none()
                if inventory:
                    # 累加在途数量
                    inventory.in_transit_qty += item["qty"]
        
        await self.db.commit()
    
    async def check_replenishment_needed(self, sku_id: str) -> tuple[bool, str]:
        """检查是否需要补货"""
        result = await self.db.execute(
            select(InventoryView).where(InventoryView.sku_id == sku_id)
        )
        inventory = result.scalar_one_or_none()
        
        if not inventory:
            return False, "SKU不存在"
        
        if inventory.available_qty < inventory.reorder_point:
            return True, f"可用库存{inventory.available_qty} < 补货点{inventory.reorder_point}"
        
        return False, "库存充足"
```

**Step 2: 创建测试**

```python
@pytest.mark.asyncio
async def test_sync_from_oms():
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock()
    mock_db.commit = AsyncMock()
    
    mock_oms = AsyncMock()
    mock_oms.list_inventory.return_value = [
        type('Obj', (), {
            'sku_id': 'SKU001',
            'sku_name': '产品A',
            'sellable_qty': 100,
            'reserved_qty': 20,
            'available_qty': 80
        })()
    ]
    
    mock_srm = AsyncMock()
    
    service = InventorySyncService(mock_db, mock_oms, mock_srm)
    await service.sync_from_oms()
    
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_check_replenishment_needed():
    mock_db = AsyncMock()
    mock_oms = AsyncMock()
    mock_srm = AsyncMock()
    
    service = InventorySyncService(mock_db, mock_oms, mock_srm)
    
    # Mock inventory
    mock_inventory = MagicMock()
    mock_inventory.available_qty = 50
    mock_inventory.reorder_point = 100
    
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none.return_value = mock_inventory
    mock_db.execute.return_value = mock_result
    
    needs_replenishment, reason = await service.check_replenishment_needed("SKU001")
    
    assert needs_replenishment == True
    assert "50 < 100" in reason
```

**Step 3: Run test**

Run: `pytest tests/services/test_inventory_sync_service.py -v`
Expected: 2 passed

**Step 4: Commit**

```bash
git add irp/services/inventory_sync_service.py tests/services/test_inventory_sync_service.py
git commit -m "feat: add inventory sync service"
```

---

### Task 19: 补货触发服务

**Files:**
- Create: `irp/services/replenishment_service.py`
- Create: `tests/services/test_replenishment_service.py`

**Step 1: 创建补货触发服务**

```python
import uuid
from datetime import datetime, timedelta
from irp.models.inventory import ReplenishmentTask
from irp.integrations.srm_client import SRMClient

class ReplenishmentService:
    """补货服务 - 库存低于阈值时触发补货流程"""
    
    def __init__(self, db, srm_client: SRMClient, inventory_sync_service):
        self.db = db
        self.srm = srm_client
        self.inventory_sync = inventory_sync_service
    
    async def check_and_create_replenishment(self, sku_id: str) -> tuple[bool, str]:
        """检查库存并创建补货任务"""
        needs_replenishment, reason = await self.inventory_sync.check_replenishment_needed(sku_id)
        
        if not needs_replenishment:
            return False, reason
        
        # 获取库存信息
        inventory = await self.get_inventory(sku_id)
        
        # 创建补货任务
        task = ReplenishmentTask(
            task_id=f"RPT-{uuid.uuid4().hex[:8]}",
            sku_id=sku_id,
            qty=inventory.reorder_qty,
            status="待采购",
            estimated_arrival=datetime.utcnow() + timedelta(days=inventory.lead_time_days)
        )
        
        self.db.add(task)
        await self.db.commit()
        
        return True, f"补货任务已创建: {task.task_id}"
    
    async def initiate_procurement(self, task_id: str) -> str:
        """发起采购流程"""
        result = await self.db.execute(
            select(ReplenishmentTask).where(ReplenishmentTask.task_id == task_id)
        )
        task = result.scalar_one_or_none()
        
        if not task:
            raise ValueError(f"任务不存在: {task_id}")
        
        if task.status != "待采购":
            raise ValueError(f"任务状态错误: {task.status}")
        
        # 调用 SRM 进行多平台询价
        price_comparison = await self.srm.get_price_comparison(task.sku_id, task.qty)
        
        # 生成采购申请
        requisition_id = await self.srm.create_purchase_requisition([
            {
                "sku_id": task.sku_id,
                "qty": task.qty,
                "preferred_supplier_id": task.supplier_id
            }
        ])
        
        task.requisition_id = requisition_id
        task.status = "待人工确认"
        await self.db.commit()
        
        return requisition_id
    
    async def approve_and_order(self, task_id: str) -> str:
        """人工审批后正式下单"""
        result = await self.db.execute(
            select(ReplenishmentTask).where(ReplenishmentTask.task_id == task_id)
        )
        task = result.scalar_one_or_none()
        
        if not task or not task.requisition_id:
            raise ValueError("任务或采购申请不存在")
        
        # 调用 SRM 确认采购订单
        po_id = await self.srm.confirm_purchase_order(task.requisition_id)
        
        task.status = "采购中"
        await self.db.commit()
        
        return po_id
```

**Step 2: 创建测试**

```python
@pytest.mark.asyncio
async def test_create_replenishment_task():
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()
    mock_db.execute = AsyncMock()
    
    mock_srm = AsyncMock()
    
    mock_inv_sync = AsyncMock()
    mock_inv_sync.check_replenishment_needed.return_value = (True, "需要补货")
    
    # Mock inventory
    mock_inventory = MagicMock()
    mock_inventory.reorder_qty = 100
    mock_inventory.lead_time_days = 7
    
    mock_inv_sync.get_inventory = AsyncMock(return_value=mock_inventory)
    
    service = ReplenishmentService(mock_db, mock_srm, mock_inv_sync)
    
    result, msg = await service.check_and_create_replenishment("SKU001")
    
    assert result == True
    mock_db.add.assert_called_once()
```

**Step 3: Run test**

Run: `pytest tests/services/test_replenishment_service.py -v`
Expected: 1 passed

**Step 4: Commit**

```bash
git add irp/services/replenishment_service.py tests/services/test_replenishment_service.py
git commit -m "feat: add replenishment trigger service"
```

---

## Phase 4: 人力池 + AI技能

### Task 20: 人力池模型

**Files:**
- Create: `irp/models/resource.py`
- Create: `tests/models/test_resource.py`

**Step 1: 创建人力资源模型**

```python
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

class ResourceType(str, enum.Enum):
    HUMAN = "human"
    AI = "ai"

class ResourceStatus(str, enum.Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    UNAVAILABLE = "unavailable"

class HumanResource(Base):
    __tablename__ = "human_resource"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_id = Column(String, unique=True, nullable=False, index=True)
    type = Column(String, default="human")  # human/ai
    owner = Column(String)  # PMS/SRM/OMS
    owner_id = Column(String)  # 原始ID
    
    # 基础
    name = Column(String, nullable=False)
    
    # 人力专有
    skills = Column(JSON, default=list)  # 技能标签列表
    availability = Column(Float, default=1.0)  # 0-1
    current_projects = Column(JSON, default=list)
    department = Column(String)
    role = Column(String)
    
    # AI专有
    if type == "ai":
        skill_packages = Column(JSON, default=list)  # 技能包
        capability_level = Column(String)  # 基础/高级/专业
        api_endpoint = Column(String)
        cost_per_call = Column(Float, default=0)
    
    # 调度偏好
    preferred_task_types = Column(JSON, default=list)
    excluded_tasks = Column(JSON, default=list)
    
    # 状态
    status = Column(String, default="available")  # available/busy/unavailable
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TaskRequest(Base):
    __tablename__ = "task_request"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(String, unique=True, nullable=False, index=True)
    task_type = Column(String, nullable=False)
    
    # 需求特征
    features = Column(JSON, default=dict)  # {
need_judgment, need_creativity, ...}
    
    # 约束
    constraints = Column(JSON, default=dict)  # {deadline, max_cost, required_skills}
    
    # 偏好
    preferences = Column(JSON, default=dict)  # {prefer_human, prefer_ai, ...}
    
    # 优先级
    priority = Column(String, default="P2")  # P0/P1/P2/P3
    
    # 状态
    status = Column(String, default="pending")  # pending/allocated/running/completed/cancelled
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**Step 2: 创建测试**

```python
def test_human_resource_creation():
    resource = HumanResource(
        resource_id="RES001",
        type="human",
        name="张三",
        skills=["Python", "项目管理"],
        availability=0.8,
        department="研发部",
        status="available"
    )
    assert resource.name == "张三"
    assert "Python" in resource.skills

def test_ai_resource_creation():
    resource = HumanResource(
        resource_id="AI001",
        type="ai",
        name="数据分析AI",
        skill_packages=["数据分析", "报表生成"],
        capability_level="高级",
        cost_per_call=0.01,
        status="available"
    )
    assert resource.type == "ai"
    assert resource.cost_per_call == 0.01
```

**Step 3: Run test**

Run: `pytest tests/models/test_resource.py -v`
Expected: 2 passed

**Step 4: Commit**

```bash
git add irp/models/resource.py tests/models/test_resource.py
git commit -m "feat: add HumanResource and TaskRequest models"
```

---

### Task 21: 资源调度服务

**Files:**
- Create: `irp/services/resource_scheduler.py`
- Create: `tests/services/test_resource_scheduler.py`

**Step 1: 创建资源调度服务**

```python
from typing import List, Optional
from irp.models.resource import HumanResource, TaskRequest

class ResourceScheduler:
    """资源调度服务 - 智能分配人+AI资源"""
    
    def __init__(self, db):
        self.db = db
    
    def analyze_task_features(self, task_request: TaskRequest) -> dict:
        """分析任务特征，决定人/AI分配比例"""
        features = task_request.features or {}
        
        # 计算加权得分
        judgment_score = features.get("need_judgment", 0.5)
        creativity_score = features.get("need_creativity", 0.5)
        data_intensive_score = features.get("data_intensive", 0.5)
        repeatability_score = features.get("repeatability", 0.5)
        
        # 创意/判断型 → 偏人力
        human_score = (judgment_score * 0.4 + creativity_score * 0.4 + 
                      (1 - data_intensive_score) * 0.1 + 
                      (1 - repeatability_score) * 0.1)
        
        # 数据/重复型 → 偏AI
        ai_score = (data_intensive_score * 0.4 + repeatability_score * 0.4 +
                   (1 - judgment_score) * 0.1 + 
                   (1 - creativity_score) * 0.1)
        
        # 归一化
        total = human_score + ai_score
        human_ratio = human_score / total if total > 0 else 0.5
        ai_ratio = ai_score / total if total > 0 else 0.5
        
        return {
            "human_ratio": human_ratio,
            "ai_ratio": ai_ratio,
            "recommended_approach": "human" if human_ratio > ai_ratio else "ai"
        }
    
    async def find_matching_resources(self, task_request: TaskRequest, 
                                     resource_type: str) -> List[HumanResource]:
        """查找匹配的资源"""
        constraints = task_request.constraints or {}
        required_skills = constraints.get("required_skills", [])
        
        query = select(HumanResource).where(
            HumanResource.type == resource_type,
            HumanResource.status == "available"
        )
        
        result = await self.db.execute(query)
        all_resources = result.scalars().all()
        
        # 按技能匹配度过滤
        if required_skills and resource_type == "human":
            matched = []
            for resource in all_resources:
                resource_skills = resource.skills or []
                if any(skill in resource_skills for skill in required_skills):
                    matched.append(resource)
            return matched
        
        return list(all_resources)
    
    async def allocate_task(self, task_request: TaskRequest) -> dict:
        """为任务分配资源"""
        # 1. 分析任务特征
        analysis = self.analyze_task_features(task_request)
        
        # 2. 查找匹配的人力和AI资源
        human_resources = await self.find_matching_resources(task_request, "human")
        ai_resources = await self.find_matching_resources(task_request, "ai")
        
        # 3. 生成分配方案
        human_ratio = analysis["human_ratio"]
        ai_ratio = analysis["ai_ratio"]
        
        allocation = {
            "task_id": task_request.task_id,
            "analysis": analysis,
            "human_allocation": None,
            "ai_allocation": None,
            "confidence": 0.7 if (human_resources and ai_resources) else 0.4,
            "reasoning": ""
        }
        
        if human_resources and human_ratio > 0.3:
            allocation["human_allocation"] = {
                "resource_id": human_resources[0].resource_id,
                "name": human_resources[0].name,
                "ratio": human_ratio,
                "time_estimate_hours": 4
            }
        
        if ai_resources and ai_ratio > 0.3:
            allocation["ai_allocation"] = {
                "resource_id": ai_resources[0].resource_id,
                "name": ai_resources[0].name,
                "ratio": ai_ratio,
                "time_estimate_hours": 1
            }
        
        # 4. 生成推荐理由
        if allocation["human_allocation"] and allocation["ai_allocation"]:
            allocation["reasoning"] = "混合方案：AI处理数据，人力处理创意和判断"
        elif allocation["human_allocation"]:
            allocation["reasoning"] = f"人力方案：推荐 {human_resources[0].name}"
        elif allocation["ai_allocation"]:
            allocation["reasoning"] = f"AI方案：{ai_resources[0].name} 自动处理"
        else:
            allocation["reasoning"] = "无可用资源，请人工分配"
            allocation["confidence"] = 0.1
        
        return allocation
```

**Step 2: 创建测试**

```python
@pytest.mark.asyncio
async def test_analyze_task_features():
    scheduler = ResourceScheduler(None)
    
    # 高数据密集型任务 → 偏AI
    task = MagicMock()
    task.features = {
        "need_judgment": 0.2,
        "need_creativity": 0.2,
        "data_intensive": 0.9,
        "repeatability": 0.8
    }
    
    analysis = scheduler.analyze_task_features(task)
    
    assert analysis["recommended_approach"] == "ai"
    assert analysis["ai_ratio"] > analysis["human_ratio"]

@pytest.mark.asyncio
async def test_allocate_task():
    mock_db = AsyncMock()
    scheduler = ResourceScheduler(mock_db)
    
    # Mock task request
    mock_task = MagicMock()
    mock_task.task_id = "TASK001"
    mock_task.features = {"need_judgment": 0.8, "need_creativity": 0.6, "data_intensive": 0.3, "repeatability": 0.2}
    mock_task.constraints = {}
    mock_task.preferences = {}
    
    # Mock resources
    mock_human = MagicMock()
    mock_human.resource_id = "RES001"
    mock_human.name = "张三"
    mock_human.skills = ["Python", "项目管理"]
    
    mock_ai = MagicMock()
    mock_ai.resource_id = "AI001"
    mock_ai.name = "数据分析AI"
    
    # Mock db query results
    async def mock_execute(query):
        result = AsyncMock()
        if "human" in str(query):
            result.scalars.return_value.all.return_value = [mock_human]
        else:
            result.scalars.return_value.all.return_value = [mock_ai]
        return result
    
    mock_db.execute = mock_execute
    
    allocation = await scheduler.allocate_task(mock_task)
    
    assert allocation["task_id"] == "TASK001"
    assert allocation["human_allocation"] is not None
    assert allocation["ai_allocation"] is not None
```

**Step 3: Run test**

Run: `pytest tests/services/test_resource_scheduler.py -v`
Expected: 2 passed

**Step 4: Commit**

```bash
git add irp/services/resource_scheduler.py tests/services/test_resource_scheduler.py
git commit -m "feat: add resource scheduler service with human+AI allocation"
```

---

## Phase 5: 规则引擎

### Task 22: 规则引擎核心

**Files:**
- Create: `irp/services/rule_engine.py`
- Create: `tests/services/test_rule_engine.py`

**Step 1: 创建规则引擎**

```python
from typing import Any, Optional
from pydantic import BaseModel
from enum import Enum

class RuleType(str, Enum):
    HARD_CONSTRAINT = "hard_constraint"
    SOFT_RULE = "soft_rule"
    LEARNED_RULE = "learned_rule"

class RuleAction(str, Enum):
    BLOCK = "block"
    FORCE = "force"
    PREFER = "prefer"
    AVOID = "avoid"

class Rule(BaseModel):
    rule_id: str
    name: str
    description: str
    rule_type: RuleType
    condition: str  # e.g., "supplier.is_discredited == true"
    action: RuleAction
    action_params: dict = {}
    weight: float = 0.5  # for soft rules
    priority: int = 50  # for conflict resolution
    enabled: bool = True
    source: str = "system"  # system/user/learned

class RuleEngine:
    """规则引擎 - 评估硬约束和软规则"""
    
    def __init__(self):
        self.hard_constraints: list[Rule] = []
        self.soft_rules: list[Rule] = []
        self.learned_rules: list[Rule] = []
    
    def add_rule(self, rule: Rule):
        """添加规则"""
        if rule.rule_type == RuleType.HARD_CONSTRAINT:
            self.hard_constraints.append(rule)
        elif rule.rule_type == RuleType.SOFT_RULE:
            self.soft_rules.append(rule)
        else:
            self.learned_rules.append(rule)
    
    def evaluate_condition(self, condition: str, context: dict) -> bool:
        """评估条件表达式"""
        try:
            # 安全评估：只允许简单的比较操作
            # 这里用eval，实际应该用安全的表达式解析器
            safe_globals = {"true": True, "false": False, "null": None}
            return eval(condition, safe_globals, context)
        except Exception:
            return False
    
    def evaluate_hard_constraints(self, context: dict) -> tuple[bool, list[str]]:
        """评估硬约束，返回 (是否通过, 失败的规则列表)"""
        failed_rules = []
        
        for rule in self.hard_constraints:
            if not rule.enabled:
                continue
            
            if self.evaluate_condition(rule.condition, context):
                failed_rules.append(rule.name)
        
        return len(failed_rules) == 0, failed_rules
    
    def evaluate_soft_rules(self, context: dict) -> tuple[list[Rule], float]:
        """评估软规则，返回 (匹配的规则列表, 总权重分)"""
        matched_rules = []
        total_weight = 0.0
        
        for rule in self.soft_rules:
            if not rule.enabled:
                continue
            
            if self.evaluate_condition(rule.condition, context):
                matched_rules.append(rule)
                weight = rule.weight if rule.action == RuleAction.PREFER else -rule.weight
                total_weight += weight
        
        return matched_rules, total_weight
    
    def evaluate(self, context: dict) -> dict:
        """综合评估"""
        # 1. 硬约束检查
        hard_passed, failed_hard = self.evaluate_hard_constraints(context)
        
        if not hard_passed:
            return {
                "passed": False,
                "blocked": True,
                "reason": f"硬约束拦截: {', '.join(failed_hard)}",
                "recommendation": None,
                "confidence": 1.0
            }
        
        # 2. 软规则评估
        matched_soft, soft_score = self.evaluate_soft_rules(context)
        
        # 3. 学习规则
        matched_learned, learned_score = self.evaluate_soft_rules(context)
        
        # 4. 计算最终得分
        final_score = soft_score + learned_score
        
        # 5. 生成建议
        if final_score > 0.3:
            recommendation = "推荐"
            confidence = 0.7
        elif final_score < -0.3:
            recommendation = "不推荐"
            confidence = 0.7
        else:
            recommendation = "需要人工判断"
            confidence = 0.4
        
        return {
            "passed": True,
            "blocked": False,
            "reason": f"软规则得分: {final_score:.2f}",
            "matched_rules": [r.name for r in matched_soft],
            "recommendation": recommendation,
            "confidence": confidence
        }
```

**Step 2: 创建测试**

```python
def test_hard_constraint_block():
    engine = RuleEngine()
    
    # 添加硬约束：失信供应商禁止
    rule = Rule(
        rule_id="HC001",
        name="失信供应商禁止",
        description="失信供应商禁止合作",
        rule_type=RuleType.HARD_CONSTRAINT,
        condition="supplier.get('is_discredited', False) == True",
        action=RuleAction.BLOCK,
        priority=100
    )
    engine.add_rule(rule)
    
    # 测试：供应商失信
    context = {"supplier": {"is_discredited": True}}
    result = engine.evaluate(context)
    
    assert result["passed"] == False
    assert result["blocked"] == True
    assert "失信供应商禁止" in result["reason"]

def test_soft_rule_prefer():
    engine = RuleEngine()
    
    rule = Rule(
        rule_id="SR001",
        name="优先历史合作供应商",
        description="合作次数>5的供应商优先",
        rule_type=RuleType.SOFT_RULE,
        condition="supplier.get('cooperation_count', 0) > 5",
        action=RuleAction.PREFER,
        weight=0.3
    )
    engine.add_rule(rule)
    
    context = {"supplier": {"cooperation_count": 10}}
    result = engine.evaluate(context)
    
    assert result["passed"] == True
    assert result["matched_rules"] == ["优先历史合作供应商"]
```

**Step 3: Run test**

Run: `pytest tests/services/test_rule_engine.py -v`
Expected: 2 passed

**Step 4: Commit**

```bash
git add irp/services/rule_engine.py tests/services/test_rule_engine.py
git commit -m "feat: add rule engine with hard/soft rules"
```

---

## Phase 6: 任务调度

### Task 23: 任务调度器

**Files:**
- Create: `irp/services/task_scheduler.py`
- Create: `tests/services/test_task_scheduler.py`

**Step 1: 创建任务调度器**

```python
from typing import Optional
from datetime import datetime
from irp.models.resource import TaskRequest, HumanResource

class TaskPriority(str, Enum):
    P0 = "P0"  # 紧急
    P1 = "P1"  # 高
    P2 = "P2"  # 中
    P3 = "P3"  # 低

class PriorityEscalation:
    """优先级动态升级规则"""
    
    RULES = [
        {"trigger": "P2 + deadline < 2h + not_started", "action": "upgrade_to", "target": "P1"},
        {"trigger": "P1 + deadline < 30min + not_started", "action": "upgrade_to", "target": "P0"},
        {"trigger": "P0 + queued > 1h + no_assignment", "action": "notify_manager", "target": None},
    ]
    
    @classmethod
    def evaluate(cls, task: TaskRequest, current_time: datetime) -> Optional[str]:
        """评估是否需要升级"""
        if task.status != "pending":
            return None
        
        deadline = task.constraints.get("deadline") if task.constraints else None
        time_until_deadline = (deadline - current_time).total_seconds() / 3600 if deadline else None
        
        priority = task.priority
        
        # P2 -> P1
        if priority == "P2" and time_until_deadline and time_until_deadline < 2:
            return "P1"
        
        # P1 -> P0
        if priority == "P1" and time_until_deadline and time_until_deadline < 0.5:
            return "P0"
        
        return None

class TaskScheduler:
    """任务调度器 - 管理任务队列和优先级"""
    
    def __init__(self, db, resource_scheduler: ResourceScheduler, rule_engine: RuleEngine):
        self.db = db
        self.resource_scheduler = resource_scheduler
        self.rule_engine = rule_engine
    
    async def submit_task(self, task_request: TaskRequest) -> str:
        """提交任务到调度器"""
        # 1. 规则引擎评估
        context = {"task": task_request.model_dump()}
        evaluation = self.rule_engine.evaluate(context)
        
        if evaluation["blocked"]:
            task_request.status = "blocked"
            task_request.blocked_reason = evaluation["reason"]
            await self.db.commit()
            raise ValueError(f"任务被拦截: {evaluation['reason']}")
        
        # 2. 设置初始优先级
        if not task_request.priority:
            task_request.priority = "P2"
        
        # 3. 状态更新
        task_request.status = "pending"
        
        self.db.add(task_request)
        await self.db.commit()
        
        return task_request.task_id
    
    async def process_pending_tasks(self):
        """处理待处理任务队列"""
        result = await self.db.execute(
            select(TaskRequest).where(TaskRequest.status == "pending")
            .order_by(TaskRequest.priority.desc())  # P0优先
        )
        pending_tasks = result.scalars().all()
        
        processed = []
        for task in pending_tasks:
            try:
                allocation = await self.resource_scheduler.allocate_task(task)
                task.status = "allocated"
                task.allocation = allocation
                await self.db.commit()
                processed.append({"task_id": task.task_id, "allocation": allocation})
            except Exception as e:
                print(f"任务分配失败 {task.task_id}: {e}")
        
        return processed
    
    async def check_priority_escalation(self):
        """检查并执行优先级升级"""
        current_time = datetime.utcnow()
        
        result = await self.db.execute(
            select(TaskRequest).where(TaskRequest.status == "pending")
        )
        pending_tasks = result.scalars().all()
        
        escalated = []
        for task in pending_tasks:
            new_priority = PriorityEscalation.evaluate(task, current_time)
            if new_priority:
                old_priority = task.priority
                task.priority = new_priority
                escalated.append({
                    "task_id": task.task_id,
                    "old_priority": old_priority,
                    "new_priority": new_priority
                })
        
        if escalated:
            await self.db.commit()
        
        return escalated
```

**Step 2: 创建测试**

```python
def test_priority_escalation_p2_to_p1():
    task = MagicMock()
    task.status = "pending"
    task.priority = "P2"
    task.constraints = {"deadline": datetime.utcnow()}  # 已过期
    
    # 模拟 deadline < 2小时
    task.constraints = {"deadline": datetime.utcnow()}
    
    result = PriorityEscalation.evaluate(task, datetime.utcnow())
    assert result == "P1"

@pytest.mark.asyncio
async def test_submit_task_blocked():
    mock_db = AsyncMock()
    mock_db.commit = AsyncMock()
    mock_db.add = MagicMock()
    
    mock_scheduler = MagicMock()
    mock_rule_engine = MagicMock()
    mock_rule_engine.evaluate.return_value = {
        "blocked": True,
        "reason": "失信供应商禁止"
    }
    
    scheduler = TaskScheduler(mock_db, mock_scheduler, mock_rule_engine)
    
    task = MagicMock()
    task.task_id = "TASK001"
    task.priority = "P2"
    task.constraints = {}
    task.model_dump = MagicMock(return_value={})
    
    with pytest.raises(ValueError, match="任务被拦截"):
        await scheduler.submit_task(task)
```

**Step 3: Run test**

Run: `pytest tests/services/test_task_scheduler.py -v`
Expected: 2 passed

**Step 4: Commit**

```bash
git add irp/services/task_scheduler.py tests/services/test_task_scheduler.py
git commit -m "feat: add task scheduler with priority escalation"
```

---

## Phase 7: 资金流向可视化

### Task 24: 资金数据模型

**Files:**
- Create: `irp/models/fund.py`
- Create: `tests/models/test_fund.py`

**Step 1: 创建资金模型**

```python
from sqlalchemy import Column, String, Float, Date, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

class FundFlow(Base):
    __tablename__ = "fund_flow"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    record_id = Column(String, unique=True, nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    type = Column(String, nullable=False)  # 收入/支出/预算分配/转账
    
    amount = Column(Float, nullable=False)
    currency = Column(String, default="CNY")
    
    source_system = Column(String, nullable=False)  # PMS/OMS/SRM
    source_id = Column(String)  # 原始单据ID
    
    category = Column(String, index=True)  # 项目支出/采购支出/销售收入/...
    sub_category = Column(String)
    
    # 关联
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
    budget_committed = Column(Float, default=0)  # 已承诺待支付
    
    # JSON分解
    categories = Column(JSON, default=dict)
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def budget_available(self):
        return self.budget_total - self.budget_spent - self.budget_committed
```

**Step 2: 创建测试**

```python
def test_fund_flow_creation():
    flow = FundFlow(
        record_id="FF001",
        date=date(2024, 3, 1),
        type="支出",
        amount=10000.0,
        source_system="SRM",
        category="采购支出",
        supplier_id="SUP001"
    )
    assert flow.amount == 10000.0

def test_budget_view_available():
    budget = BudgetView(
        project_id="PRJ001",
        budget_total=1000000.0,
        budget_spent=300000.0,
        budget_committed=200000.0
    )
    assert budget.budget_available == 500000.0
```

**Step 3: Run test**

Run: `pytest tests/models/test_fund.py -v`
Expected: 2 passed

**Step 4: Commit**

```bash
git add irp/models/fund.py tests/models/test_fund.py
git commit -m "feat: add FundFlow and BudgetView models"
```

---

### Task 25: 资金同步服务

**Files:**
- Create: `irp/services/fund_sync_service.py`
- Create: `tests/services/test_fund_sync_service.py`

**Step 1: 创建资金同步服务**

```python
from datetime import date, timedelta
from collections import defaultdict
from irp.models.fund import FundFlow, BudgetView

class FundSyncService:
    """资金同步服务 - 从 PMS/OMS/SRM 同步资金数据"""
    
    def __init__(self, db, pms_client, oms_client, srm_client):
        self.db = db
        self.pms = pms
        self.oms = oms
        self.srm = srm
    
    async def sync_from_all_sources(self, start_date: date, end_date: date):
        """从所有来源同步资金流"""
        # 1. 从 SRM 同步采购支出
        await self.sync_from_srm(start_date, end_date)
        
        # 2. 从 OMS 同步销售收入
        await self.sync_from_oms(start_date, end_date)
        
        # 3. 从 PMS 同步项目预算
        await self.sync_from_pms(start_date, end_date)
    
    async def sync_from_srm(self, start_date, end_date):
        """从 SRM 同步采购支出"""
        invoices = await self.srm.get_invoices(start_date=start_date, end_date=end_date)
        
        for invoice in invoices:
            flow = FundFlow(
                record_id=f"SRM-INV-{invoice.invoice_id}",
                date=invoice.invoice_date,
                type="支出",
                amount=invoice.amount,
                source_system="SRM",
                source_id=invoice.invoice_id,
                category="采购支出",
                supplier_id=invoice.supplier_id,
                contract_id=invoice.contract_id
            )
            self.db.add(flow)
        
        await self.db.commit()
    
    async def get_dashboard(self, group_by: str = "month") -> dict:
        """获取资金看板"""
        # 收入总计
        income_result = await self.db.execute(
            select(func.sum(FundFlow.amount)).where(FundFlow.type == "收入")
        )
        total_income = income_result.scalar() or 0
        
        # 支出总计
        expense_result = await self.db.execute(
            select(func.sum(FundFlow.amount)).where(FundFlow.type == "支出")
        )
        total_expense = expense_result.scalar() or 0
        
        # 按维度分解
        by_dimension = await self.get_breakdown(group_by)
        
        return {
            "total_income": total_income,
            "total_expense": total_expense,
            "net_flow": total_income - total_expense,
            "by_dimension": by_dimension
        }
    
    async def get_breakdown(self, group_by: str) -> dict:
        """按维度分解资金流"""
        if group_by == "project":
            result = await self.db.execute(
                select(FundFlow.project_id, func.sum(FundFlow.amount))
                .group_by(FundFlow.project_id)
            )
            return {row[0]: row[1] for row in result.all() if row[0]}
        
        elif group_by == "supplier":
            result = await self.db.execute(
                select(FundFlow.supplier_id, func.sum(FundFlow.amount))
                .group_by(FundFlow.supplier_id)
            )
            return {row[0]: row[1] for row in result.all() if row[0]}
        
        elif group_by == "month":
            result = await self.db.execute(
                select(
                    func.date_trunc('month', FundFlow.date).label('month'),
                    func.sum(FundFlow.amount)
                ).group_by('month').order_by('month')
            )
            return {str(row[0]): row[1] for row in result.all()}
        
        return {}
```

**Step 2: 创建测试**

```python
@pytest.mark.asyncio
async def test_get_dashboard():
    mock_db = AsyncMock()
    mock_pms = AsyncMock()
    mock_oms = AsyncMock()
    mock_srm = AsyncMock()
    
    service = FundSyncService(mock_db, mock_pms, mock_oms, mock_srm)
    
    # Mock aggregate results
    mock_income_result = AsyncMock()
    mock_income_result.scalar.return_value = 1000000.0
    mock_expense_result = AsyncMock()
    mock_expense_result.scalar.return_value = 600000.0
    
    mock_db.execute.side_effect = [
        mock_income_result,
        mock_expense_result,
        AsyncMock()  # breakdown query
    ]
    
    dashboard = await service.get_dashboard()
    
    assert dashboard["total_income"] == 1000000.0
    assert dashboard["total_expense"] == 600000.0
    assert dashboard["net_flow"] == 400000.0
```

**Step 3: Run test**

Run: `pytest tests/services/test_fund_sync_service.py -v`
Expected: 1 passed

**Step 4: Commit**

```bash
git add irp/services/fund_sync_service.py tests/services/test_fund_sync_service.py
git commit -m "feat: add fund sync service with dashboard"
```

---

## Phase 8: Web 控制台

### Task 26: Web 控制台 API

**Files:**
- Create: `irp/api/dashboard.py`
- Create: `irp/templates/dashboard.html` (基础前端)

**Step 1: 创建看板 API**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from irp.core.database import get_db
from irp.services.supplier_sync_service import SupplierSyncService
from irp.services.inventory_sync_service import InventorySyncService
from irp.services.fund_sync_service import FundSyncService

router = APIRouter()

@router.get("/dashboard/overview")
async def get_overview(db: AsyncSession = Depends(get_db)):
    """获取总览看板"""
    # 供应商统计
    supplier_stats = await get_supplier_stats(db)
    
    # 库存预警
    inventory_alerts = await get_inventory_alerts(db)
    
    # 资金概览
    fund_dashboard = await get_fund_dashboard(db)
    
    # 待处理任务
    pending_tasks = await get_pending_tasks(db)
    
    return {
        "suppliers": supplier_stats,
        "inventory": inventory_alerts,
        "funds": fund_dashboard,
        "tasks": pending_tasks
    }

@router.get("/dashboard/resources")
async def get_resources_dashboard(db: AsyncSession = Depends(get_db)):
    """获取资源看板"""
    # 人力分布
    human_resources = await get_human_distribution(db)
    
    # AI技能分布
    ai_resources = await get_ai_distribution(db)
    
    return {
        "human": human_resources,
        "ai": ai_resources
    }
```

**Step 2: 创建基础 HTML 模板**

```html
<!DOCTYPE html>
<html>
<head>
    <title>IRP 控制台</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .card { border: 1px solid #ddd; padding: 15px; margin: 10px; border-radius: 8px; }
        .metric { font-size: 24px; font-weight: bold; color: #333; }
        .label { color: #666; font-size: 14px; }
        .grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }
    </style>
</head>
<body>
    <h1>IRP 智能资源管理平台</h1>
    <div class="grid">
        <div class="card">
            <div class="label">供应商总数</div>
            <div class="metric" id="supplier-total">-</div>
        </div>
        <div class="card">
            <div class="label">库存预警</div>
            <div class="metric" id="inventory-alerts">-</div>
        </div>
        <div class="card">
            <div class="label">本月支出</div>
            <div class="metric" id="monthly-expense">-</div>
        </div>
        <div class="card">
            <div class="label">待处理任务</div>
            <div class="metric" id="pending-tasks">-</div>
        </div>
    </div>
    
    <script>
        async function loadDashboard() {
            const response = await fetch('/api/v1/dashboard/overview');
            const data = await response.json();
            document.getElementById('supplier-total').textContent = data.suppliers.total;
            document.getElementById('inventory-alerts').textContent = data.inventory.alert_count;
            document.getElementById('monthly-expense').textContent = '¥' + data.funds.monthly_expense.toLocaleString();
            document.getElementById('pending-tasks').textContent = data.tasks.pending_count;
        }
        loadDashboard();
    </script>
</body>
</html>
```

**Step 3: Commit**

```bash
git add irp/api/dashboard.py irp/templates/dashboard.html
git commit -m "feat: add dashboard API and basic HTML frontend"
```

---

## Phase 9: 规则学习 (进阶)

### Task 27: 规则学习服务

**Files:**
- Create: `irp/services/rule_learning_service.py`
- Create: `tests/services/test_rule_learning_service.py`

**Step 1: 创建规则学习服务**

```python
from collections import defaultdict
from irp.models.rule_learning import LearnedPattern, HumanDecision

class RuleLearningService:
    """规则学习服务 - 从人工决策中学习规则"""
    
    def __init__(self, db):
        self.db = db
        self.min_samples = 5  # 最少样本数
        self.confidence_threshold = 0.7  # 置信度阈值
    
    async def record_decision(self, context: dict, decision: str, outcome: str):
        """记录人工决策"""
        record = HumanDecision(
            context=context,
            decision=decision,
            outcome=outcome,
            created_at=datetime.utcnow()
        )
        self.db.add(record)
        await self.db.commit()
        
        # 检查是否需要生成规则
        await self.check_and_create_rule(context, decision)
    
    async def check_and_create_rule(self, context: dict, decision: str):
        """检查是否满足规则生成条件"""
        # 查找相似的历史决策
        similar = await self.find_similar_decisions(context)
        
        if len(similar) < self.min_samples:
            return None
        
        # 检查决策一致性
        decisions = [s.decision for s in similar]
        decision_ratio = decisions.count(decision) / len(decisions)
        
        if decision_ratio >= self.confidence_threshold:
            # 生成学习规则
            rule = LearnedRule(
                pattern=self.extract_pattern(context),
                suggested_action=decision,
                confidence=decision_ratio,
                sample_count=len(similar),
                status="candidate"  # 待审核
            )
            self.db.add(rule)
            await self.db.commit()
            return rule
        
        return None
    
    async def find_similar_decisions(self, context: dict) -> list:
        """查找相似的历史决策"""
        # 简化版：基于关键字段匹配
        supplier_id = context.get("supplier_id")
        
        result = await self.db.execute(
            select(HumanDecision)
            .where(HumanDecision.context.contains({"supplier_id": supplier_id}))
            .order_by(HumanDecision.created_at.desc())
            .limit(20)
        )
        
        return result.scalars().all()
    
    def extract_pattern(self, context: dict) -> dict:
        """从上下文提取模式"""
        return {
            "supplier_risk_level": context.get("supplier_risk_level"),
            "supplier_rating": context.get("supplier_rating"),
            "order_amount_range": context.get("order_amount_range"),
            "decision_trigger": context.get("decision_trigger")
        }
    
    async def approve_rule(self, rule_id: str):
        """审核通过学习规则"""
        result = await self.db.execute(
            select(LearnedRule).where(LearnedRule.id == rule_id)
        )
        rule = result.scalar_one_or_none()
        
        if rule:
            rule.status = "active"
            # 添加到规则引擎
            from irp.services.rule_engine import Rule, RuleType, RuleAction
            new_rule = Rule(
                rule_id=f"LEARNED-{rule_id}",
                name=f"学习规则: {rule.pattern}",
                description=f"从{rule.sample_count}次决策中学习",
                rule_type=RuleType.LEARNED_RULE,
                condition=self.build_condition(rule.pattern),
                action=RuleAction.PREFER if "approve" in rule.suggested_action else RuleAction.AVOID,
                weight=rule.confidence,
                source="learned"
            )
            await self.db.commit()
            return new_rule
        
        return None
```

**Step 2: 创建测试**

```python
@pytest.mark.asyncio
async def test_record_decision():
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()
    mock_db.execute = AsyncMock()
    
    service = RuleLearningService(mock_db)
    
    context = {
        "supplier_id": "SUP001",
        "supplier_risk_level": "低",
        "order_amount": 50000
    }
    
    await service.record_decision(context, "approve", "success")
    
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_check_and_create_rule():
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()
    
    # Mock similar decisions
    mock_decisions = [
        MagicMock(decision="approve", context={}),
        MagicMock(decision="approve", context={}),
        MagicMock(decision="approve", context={}),
        MagicMock(decision="approve", context={}),
        MagicMock(decision="approve", context={}),
    ]
    mock_result = AsyncMock()
    mock_result.scalars.return_value.all.return_value = mock_decisions
    mock_db.execute.return_value = mock_result
    
    service = RuleLearningService(mock_db)
    service.min_samples = 3
    service.confidence_threshold = 0.8
    
    result = await service.check_and_create_rule({"supplier_id": "SUP001"}, "approve")
    
    # 应该创建规则 (5个approve，100%一致)
    assert result is not None
    assert result.status == "candidate"
```

**Step 3: Run test**

Run: `pytest tests/services/test_rule_learning_service.py -v`
Expected: 2 passed

**Step 4: Commit**

```bash
git add irp/services/rule_learning_service.py tests/services/test_rule_learning_service.py
git commit -m "feat: add rule learning service for pattern extraction"
```

---

## 总结

**Phase 1-4 实现完成后的能力**:

| Phase | 能力 | Task数 |
|-------|------|--------|
| Phase 1 | 基础设施 + 三大系统集成 + 供应商主数据 | 13 |
| Phase 2 | 合同中心 | 3 |
| Phase 3 | 库存视图 + 触发补货 | 3 |
| Phase 4 | 人力池 + AI技能 + 资源调度 | 3 |
| Phase 5 | 规则引擎 | 1 |
| Phase 6 | 任务调度 | 1 |
| Phase 7 | 资金流向可视化 | 2 |
| Phase 8 | Web控制台 | 1 |
| Phase 9 | 规则学习 | 1 |
| **总计** | | **28** |

**完整能力矩阵**:

```
✅ 供应商主数据 (SRM为主)
✅ 合同中心 (树状结构 + 审批流)
✅ 库存视图 (OMS+SRM联动)
✅ 触发式补货 (半自动)
✅ 人力池 (PMS + AI技能)
✅ 资源调度 (人+AI混合)
✅ 规则引擎 (硬约束 + 软规则)
✅ 任务调度 (P0-P3 + 动态升级)
✅ 资金流向可视化 (多维度)
✅ Web控制台 (基础)
✅ 规则学习 (从人工决策提取)
```

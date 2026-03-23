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

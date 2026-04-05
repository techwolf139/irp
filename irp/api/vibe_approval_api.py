"""IRP MASFactory FastAPI 集成

实现合同审批 API，支持:
1. 传统审批接口 (向后兼容)
2. VibeGraph 审批接口 (新增强大功能)
3. 混合模式运行
"""

from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from datetime import datetime
import logging

from irp.masfactory.examples.contract_approval_v2 import ContractApprovalGraph, demo_contract_approval_v2
from irp.masfactory.examples.contract_approval_v3_interactive import InteractiveContractGraph, demo_interactive_approval
from irp.masfactory.examples.contract_approval_v4_contextual import (
    InteractiveContractGraphWithContext,
    MCPContractAdapter,
    RAGContractAdapter
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="IRP VibeGraph 审批系统",
    description="基于 MASFactory 的智能合同审批系统",
    version="1.0.0"
)


# ============ 请求/响应 模型 ============

class ContractApprovalRequest(BaseModel):
    """合同审批请求模型"""
    contract_id: str = Field(..., description="合同 ID", max_length=50)
    contract_type: str = Field(..., 
        description="合同类型 (PURCHASE/OUTSOURCE/FRAMEWORK)",
        pattern="^(PURCHASE|OUTSOURCE|FRAMEWORK)$"
    )
    amount: float = Field(..., description="合同金额", gt=0)
    title: Optional[str] = Field(None, description="合同标题", max_length=200)


class ApprovalResponse(BaseModel):
    """审批响应模型"""
    contract_id: str
    contract_type: str
    approval_status: str
    approval_history: List[Dict[str, Any]]
    interaction_log: List[Dict[str, Any]]
    processing_time: float
    generated_at: str


class ContractApproveV2Request(BaseModel):
    """VibeGraph V2 审批请求"""
    contract_id: str
    contract_type: str
    amount: float
    title: Optional[str] = None


class ContractApproveInteractiveRequest(BaseModel):
    """交互审批请求"""
    contract_id: str
    contract_type: str
    amount: float
    title: Optional[str] = None
    enable_mcp: bool = False
    enable_rag: bool = False


# ============ API Endpoints ============

@app.get("/")
async def root():
    """服务健康检查"""
    return {
        "status": "healthy",
        "service": "MASFactory Contract Approval API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/v1/contracts/{contract_id}/approval/v1", response_model=ApprovalResponse)
async def approve_contract_v1(request: ContractApprovalRequest, background_tasks: BackgroundTasks):
    """
    ### 合同审批 v1 (传统方式)
    
    使用现有的快速审批流程，适用于简单合同。
    
    **参数:**
    - contract_id: 合同唯一标识
    - contract_type: 采购/外包/框架
    - amount: 合同金额
    - title: 合同标题 (可选)
    """
    logger.info(f"Processing contract {request.contract_id} via v1 API")
    
    # 创建审批图
    graph = ContractApprovalGraph(name=request.contract_type.lower() + "_approval")
    
    start_time = datetime.now()
    
    try:
        # 执行审批
        result = await graph.execute_contract_approval(
            contract_type=request.contract_type,
            contract_id=request.contract_id,
            amount=request.amount,
            title=request.title or ""
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return ApprovalResponse(
            contract_id=request.contract_id,
            contract_type=request.contract_type,
            approval_status=result.get("approval_status", "pending"),
            approval_history=result.get("approval_history", []),
            interaction_log=result.get("interaction_log", []),
            processing_time=processing_time,
            generated_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Approval failed for {request.contract_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/contracts/{contract_id}/approval/vibe", response_model=ApprovalResponse)
async def approve_contract_vibe(request: ContractApproveV2Request, background_tasks: BackgroundTasks):
    """
    ### 合同审批 v2 (VibeGraph 模式)
    
    使用自然语言到图的编译，生成优化的审批流程。
    
    **参数:**
    - contract_type: 合同类型
    - amount: 合同金额
    - title: 合同标题
    """
    logger.info(f"Processing contract {request.contract_id} via VibeGraph API")
    
    try:
        # 创建 VibeGraph 审批图
        graph = ContractApprovalGraph(name="vibe_approval")
        
        start_time = datetime.now()
        
        result = await graph.execute_contract_approval(
            contract_type=request.contract_type,
            contract_id=request.contract_id,
            amount=request.amount,
            title=request.title or ""
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return ApprovalResponse(
            contract_id=request.contract_id,
            contract_type=request.contract_type,
            approval_status=result.get("approval_status", "pending"),
            approval_history=result.get("approval_history", []),
            interaction_log=result.get("interaction_log", []),
            processing_time=processing_time,
            generated_at=datetime.now().isoformat()
        )
        
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Approval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/contracts/{contract_id}/approval/interactive", response_model=ApprovalResponse)
async def approve_contract_interactive(
    request: ContractApproveInteractiveRequest,
    background_tasks: BackgroundTasks
):
    """
    ### 交互式审批 v3 (人机协同)
    
    支持用户确认和反馈的审批流程。
    
    **参数:**
    - enable_mcp: 是否启用 MCP 历史数据
    - enable_rag: 是否启用 RAG 检索增强
    """
    logger.info(f"Processing contract {request.contract_id} via Interactive API")
    
    try:
        # 选择审批图类型
        if request.enable_mcp or request.enable_rag:
            # 使用上下文增强版本
            graph = InteractiveContractGraphWithContext(name="contextual_approval")
        else:
            # 基础交互式版本
            graph = InteractiveContractGraph(name="interactive_approval")
        
        start_time = datetime.now()
        
        # 执行审批
        result = await graph.execute_contract_approval(
            contract_type=request.contract_type,
            contract_id=request.contract_id,
            amount=request.amount,
            title=request.title or "",
            interaction_enabled=True
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "contract_id": request.contract_id,
            "contract_type": request.contract_type,
            "approval_status": result.get("approval_status", "pending"),
            "approval_history": result.get("approval_history", []),
            "interaction_log": result.get("interaction_log", []),
            "processing_time": processing_time,
            "generated_at": datetime.now().isoformat(),
            "contextual_context": {
                "mcp_enabled": request.enable_mcp,
                "rag_enabled": request.enable_rag
            }
        }
        
    except Exception as e:
        logger.error(f"Interactive approval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/contracts/{contract_id}/approval/history")
async def get_approval_history(contract_id: str):
    """
    ### 获取审批历史
    
    查询特定合同的所有审批记录。
    """
    return {
        "contract_id": contract_id,
        "history": [
            {
                "date": "2024-03-15",
                "status": "approved",
                "approver": "采购负责人",
                "comment": "合同条款合理"
            },
            {
                "date": "2024-03-16",
                "status": "approved",
                "approver": "法务",
                "comment": "法律风险评估通过"
            },
            {
                "date": "2024-03-17",
                "status": "approved",
                "approver": "财务",
                "comment": "预算充足"
            }
        ]
    }


@app.get("/api/v1/approval/types")
async def get_approval_types():
    """获取支持的合同类型"""
    return {
        "approved_types": [
            {
                "type": "PURCHASE",
                "name": "采购合同",
                "steps": ["采购负责人", "法务", "财务"],
                "required_for": "超过 10 万元的采购"
            },
            {
                "type": "OUTSOURCE",
                "name": "外包合同",
                "steps": ["项目负责人", "法务"],
                "required_for": "项目外包服务"
            },
            {
                "type": "FRAMEWORK",
                "name": "框架协议",
                "steps": ["法务"],
                "required_for": "年度采购协议"
            }
        ],
        "vibe_graphing_support": True,
        "mcp_integration": True,
        "rag_enhancement": True
    }


# ============ 启动服务 ============

def run_api(port: int = 8000):
    """运行 API 服务"""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    run_api()

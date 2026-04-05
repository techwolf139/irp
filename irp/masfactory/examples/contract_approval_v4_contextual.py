"""合同审批 v4 - MCP/RAG 集成版本

在 v3 基础上新增:
1. MCP (Model Context Protocol) 集成
2. RAG (检索增强生成) 支持
3. 外部知识库查询
4. 合同历史数据检索
"""

from typing import Any, Dict, List, Optional
import json
from datetime import datetime

from irp.mas_factory.core.graph import Graph
from irp.mas_factory.core.agent import Agent, AgentDefinition
from irp.mas_factory.core.state import State
from irp.mas_factory.adapters.context import ContextAdapter, ContextBlock


class MCPContractAdapter(ContextAdapter):
    """MCP 合同适配器
    
    用于集成企业知识库和合同历史数据
    """
    
    def __init__(self, name: str = "contract_mcp"):
        super().__init__(name=name, context_label="MCP_CONTRACT")
    
    def validate(self) -> bool:
        """验证 MCP 适配器"""
        return True

    
    async def load_contract_history(self, contract_type: str, amount: float) -> Dict[str, Any]:
        """加载合同历史数据"""
        # 简化版：返回模拟的历史数据
        return {
            "contract_type": contract_type,
            "historical_similar": [
                {
                    "contract_id": "CON2023001",
                    "amount": amount * 0.8,
                    "approval_time": "3 days",
                    "status": "approved"
                },
                {
                    "contract_id": "CON2023002", 
                    "amount": amount,
                    "approval_time": "5 days",
                    "status": "with_conditions"
                }
            ],
            "similar_amount_range": "80%-120%",
            "average_approval_days": 4
        }
    
    async def load_legal_database(self) -> Dict[str, Any]:
        """加载法律数据库知识"""
        return {
            "legal_requirements": [
                "所有合同必须包含完整的双方信息",
                "金额超过 50 万需要法务审批",
                "外包合同必须明确交付时间和质量标准"
            ],
            "compliance_checklist": [
                "合同条款完备性",
                "法律风险评估",
                "合规性审核"
            ]
        }
    
    async def load_context(self, state: State) -> Dict[str, Any]:
        """从 MCP 加载上下文"""
        contract_type = state.get("contract_type", "")
        amount = state.get("amount", 0)
        
        if not amount:
            return {}
        
        # 加载历史数据
        history = await self.load_contract_history(contract_type, amount)
        
        # 加载法律知识
        legal_db = await self.load_legal_database()
        
        return {
            "contract_type": contract_type,
            "historical_data": history,
            "legal_requirements": legal_db["legal_requirements"],
            "compliance_checklist": legal_db["compliance_checklist"]
        }


class RAGContractAdapter(ContextAdapter):
    """RAG 合同知识库适配器
    
    用于检索相似合同案例和最佳实践
    """
    
    def __init__(self, name: str = "contract_rag"):
        super().__init__(name=name, context_label="RAG_CONTRACT")
    
    def validate(self) -> bool:
        """验证 RAG 适配器"""
        return True

    
    def build_query_vector(self, contract_type: str, amount: float) -> str:
        """构建查询向量"""
        return f"{contract_type} contract amount {amount}"
    
    async def search_similar_contracts(self, query: str, top_k: int = 3) -> List[ContextBlock]:
        """搜索相似合同"""
        # 简化版：返回模拟搜索结果
        return [
            ContextBlock(
                text=f"Similar contract case for: {query}",
                score=0.95,
                uri=f"rag://contracts/similar/{1}"
            ),
            ContextBlock(
                text="Best practice: All procurement contracts must include detailed scope.",
                score=0.85,
                uri=f"rag://contracts/practice/1"
            ),
            ContextBlock(
                text="Risk analysis: High value contracts may require additional legal review.",
                score=0.72,
                uri=f"rag://contracts/risk/high_value"
            )
        ]
    
    async def load_context(self, state: State) -> Dict[str, Any]:
        """从 RAG 加载上下文"""
        contract_type = state.get("contract_type", "")
        amount = state.get("amount", 0)
        
        if not amount or not contract_type:
            return {}
        
        query = self.build_query_vector(contract_type, amount)
        results = await self.search_similar_contracts(query, top_k=3)
        
        return {
            "relevant_cases": [block.to_dict() for block in results],
            "retrieval_query": query
        }


class InteractiveContractGraphWithContext(Graph):
    """带有 MCP/RAG 集成的交互式审批图"""
    
    def __init__(self, name: str = "contextual_approval"):
        super().__init__(name=name)
        
        self.roles = {
            "PURCHASE": ["采购负责人", "法务", "财务"],
            "OUTSOURCE": ["项目负责人", "法务"],
            "FRAMEWORK": ["法务"],
        }
        
        # 初始化上下文适配器
        self.contract_history_adapter = MCPContractAdapter("contract_history")
        self.legal_rag_adapter = RAGContractAdapter("legal_rag")
        
        self._init_roles_graph()
        self._init_interactive_nodes()
        self._create_edges()
    
    async def _prepare_contextual_approval(self, state: State) -> Dict[str, Any]:
        """准备带上下文的审批"""
        # 加载 MCP 上下文
        mcp_context = await self.contract_history_adapter.load_context(state)
        
        # 加载 RAG 上下文
        rag_context = await self.legal_rag_adapter.load_context(state)
        
        # 合并上下文
        return {
            "mcp_data": mcp_context,
            "rag_data": rag_context,
            "approval_timestamp": datetime.now().isoformat()
        }
    
    def _init_roles_graph(self) -> None:
        """初始化角色节点 (带上下文感知)"""
        for role in ["采购负责人", "项目负责人", "法务", "财务"]:
            agent_def = AgentDefinition(
                name=f"{role}_agent",
                description=f"{role} - 专业审批 (上下文感知)",
                skills=["合同审核", "风险评估", "合规性检查", "历史数据分析"],
                instructions=f"""你是 {role}，请在审批时考虑以下信息：

                上下文数据:
                {{context}}
                
                任务：
                1. 参考历史相似合同进行对比
                2. 检查法律要求合规性
                3. 识别潜在风险
                4. 生成审批意见
                """
            )
            
            node = Agent(name=f"node_{role}", agent_def=agent_def)
            self.create_node(f"node_{role}", node)
    
    def _init_interactive_nodes(self) -> None:
        """初始化交互节点"""
        confirm_agent_def = AgentDefinition(
            name="review_confirmer",
            description="审批结果确认 (增强版)",
            skills=["结果确认", "用户交互", "上下文分析"],
            instructions="综合所有上下文信息，帮助用户理解审批依据"
        )
        
        confirm_node = Agent(
            name="node_review_confirmer",
            agent_def=confirm_agent_def
        )
        self.create_node("node_review_confirmer", confirm_node)
    
    def _create_edges(self) -> None:
        """创建审批流程图"""
        self.create_edge("ENTRY", "node_type_router")
        
        for role in ["采购负责人", "项目负责人", "法务"]:
            self.create_edge("node_type_router", f"node_{role}")
        
        self.create_edge("node_采购负责人", "node_法务")
        self.create_edge("node_项目负责人", "node_法务")
        self.create_edge("node_法务", "node_财务")
        
        self.create_edge("node_财务", "node_review_confirmer")
        self.create_edge("node_法务", "node_review_confirmer")
        
        self.create_edge("node_review_confirmer", "EXIT")


async def demo_contextual_approval():
    """演示带 MCP/RAG 的审批"""
    print("=" * 60)
    print("上下文感知审批演示 (MCP+RAG)")
    print("=" * 60)
    
    graph = InteractiveContractGraphWithContext(name="contextual_purchase")
    
    result = await graph.execute_contract_approval(
        contract_type="PURCHASE",
        contract_id="CON2024003",
        amount=300000.0,
        title="2024 Q3 采购合同"
    )
    
    print("\n✅ 上下文上下文集成完成: MCP 历史数据 + RAG 检索结果")
    print(f"合同 ID: {result.get('contract_id')}")
    print(f"审批路径：{len(result.get('approval_history', []))} 步")

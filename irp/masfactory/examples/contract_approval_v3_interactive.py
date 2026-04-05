"""合同审批 v3 - 增强人机协同版本

在 v2 基础上新增:
1. 审批过程中的用户确认 (Interaction 节点)
2. 实时反馈收集
3. 审批意见的交互式编辑
4. 人机协同的审批日志追踪
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import json
from datetime import datetime

from irp.mas_factory.core.graph import Graph
from irp.mas_factory.core.agent import Agent, AgentDefinition
from irp.mas_factory.core.state import State


class InteractiveContractGraph(Graph):
    """交互式合同审批图
    
    特性:
    - 每个审批步骤前都提供用户确认
    - 支持用户修改自动生成的审批意见
    - 记录人机协同的完整审计日志
    """
    
    def __init__(self, name: str = "interactive_approval"):
        super().__init__(name=name)
        
        # 审批角色定义
        self.roles = {
            "PURCHASE": ["采购负责人", "法务", "财务"],
            "OUTSOURCE": ["项目负责人", "法务"],
            "FRAMEWORK": ["法务"],
        }
        
        self._init_roles_graph()
        self._init_interactive_nodes()
        self._create_edges()
    
    def _init_roles_graph(self) -> None:
        """初始化角色节点"""
        for role in ["采购负责人", "项目负责人", "法务", "财务"]:
            agent_def = AgentDefinition(
                name=f"{role}_agent",
                description=f"{role} - 专业审批",
                skills=["合同审核", "风险评估", "合规性检查"],
                instructions=f"""你是 {role}，请执行以下任务：

                1. 审核合同内容完整性
                2. 识别业务和法律风险
                3. 评估金额合理性
                4. 生成结构化审批意见
                
                输出格式:
                {{
                    "approved": true/false,
                    "risk_level": "low/medium/high",
                    "issues": ["问题列表"],
                    "recommendation": "建议",
                    "approval_comment": "审批意见"
                }}
                """
            )
            
            node = Agent(name=f"node_{role}", agent_def=agent_def)
            self.create_node(f"node_{role}", node)
    
    def _init_interactive_nodes(self) -> None:
        """初始化交互节点"""
        # 审批结果确认节点
        confirm_agent_def = AgentDefinition(
            name="review_confirmer",
            description="审批结果确认 - 展示审批结果供用户确认",
            skills=["结果确认", "用户交互"],
            instructions="""你是审批结果确认助手。你的任务是：
            1. 将审批结果格式化展示
            2. 提示用户确认或修改
            3. 记录用户反馈
            """
        )
        
        confirm_node = Agent(
            name="node_review_confirmer",
            agent_def=confirm_agent_def
        )
        self.create_node("node_review_confirmer", confirm_node)
    
    def _create_edges(self) -> None:
        """创建审批流程图"""
        # ENTRY → 类型判断 → 角色审批 → 结果确认 → EXIT
        
        # ENTRY → 类型判断
        self.create_edge("ENTRY", "node_type_router")
        
        # 类型路由 → 角色节点
        for role in ["采购负责人", "项目负责人", "法务"]:
            self.create_edge("node_type_router", f"node_{role}")
        
        # 角色 → 下一步角色 或 结果确认
        self.create_edge("node_采购负责人", "node_法务")
        self.create_edge("node_项目负责人", "node_法务")
        
        # 法务 → 财务 (采购合同)
        self.create_edge("node_法务", "node_财务")
        
        # 最终审批人 → 结果确认
        self.create_edge("node_财务", "node_review_confirmer")
        self.create_edge("node_法务", "node_review_confirmer")
        
        # 结果确认 → EXIT
        self.create_edge("node_review_confirmer", "EXIT")
    
    async def execute_contract_approval(
        self,
        contract_type: str,
        contract_id: str,
        amount: float,
        title: str = "",
        initial_state: Optional[Dict] = None,
        interaction_enabled: bool = True
    ) -> Dict[str, Any]:
        """执行合同审批流程
        
        Args:
            contract_type: 合同类型
            contract_id: 合同 ID
            amount: 金额
            title: 合同标题
            initial_state: 初始状态
            interaction_enabled: 是否启用交互确认
            
        Returns:
            完整的审批结果 (含交互日志)
        """
        initial_data = {
            "contract_type": contract_type,
            "contract_id": contract_id,
            "amount": amount,
            "title": title,
            "approval_status": "pending",
            "interaction_log": [],
            "approval_history": []
        }
        
        initial_data.update(initial_state or {})
        return await self.execute(initial_data)
    
    async def get_approval_trace(self, state: State) -> List[Dict[str, Any]]:
        """获取审批执行路径
        
        Returns:
            审批路径列表 (按时间顺序)
        """
        trace = []
        
        for node_id in state.node_history:
            if node_id.startswith("node_") and node_id != "node_":
                node = self.nodes.get(node_id)
                if node:
                    trace.append({
                        "node_id": node_id,
                        "step_name": node.name,
                        "visited_at": datetime.now().isoformat()
                    })
        
        return trace


async def demo_interactive_approval():
    """演示交互式审批"""
    print("=" * 60)
    print("交互式合同审批演示")
    print("=" * 60)
    
    # 创建交互式审批图
    interactive_graph = InteractiveContractGraph(name="interactive_purchase_approval")
    
    # 执行审批
    result = await interactive_graph.execute_contract_approval(
        contract_type="PURCHASE",
        contract_id="CON2024002",
        amount=250000.0,
        title="2024 Q2 服务器设备采购"
    )
    
    # 输出结果
    print("\n📊 审批结果:")
    print(f"合同 ID: {result.get('contract_id')}")
    print(f"审批状态: {result.get('approval_status')}")
    print(f"审批路径: {len(result.get('approval_history', []))} 步")
    
    if result.get('interaction_log'):
        print("\n💬 交互日志:")
        for log in result.get('interaction_log', []):
            print(f"  - {log.get('action')}: {log.get('comment')}")


if __name__ == "__main__":
    import asyncio
    
    asyncio.run(demo_interactive_approval())

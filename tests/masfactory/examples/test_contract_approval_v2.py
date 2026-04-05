"""ContractApprovalGraph 测试

测试合同审批 v2 的基本功能
"""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from irp.masfactory.examples.contract_approval_v2 import (
    ContractApprovalGraph,
    demo_contract_approval_v2,
)


class TestContractApprovalGraph:
    """测试 ContractApprovalGraph"""
    
    def setup_method(self):
        """每个测试前的准备"""
        self.graph = ContractApprovalGraph(name="test_approval")
    
    def test_graph_initialization(self):
        """测试图初始化"""
        assert self.graph.name == "test_approval"
        assert len(self.graph.nodes) > 0
        assert len(self.graph.edges) > 0
    
    def test_node_types(self):
        """测试节点类型"""
        node_types = [n.__class__.__name__ for n in self.graph.nodes.values()]
        assert "Agent" in node_types
    
    def test_edge_count(self):
        """测试边数量"""
        assert len(self.graph.edges) >= 5
    
    def test_contract_type_purchase(self):
        """测试采购合同审批流程"""
        with patch.object(self.graph, 'execute', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = {
                "contract_id": "CON001",
                "contract_type": "PURCHASE",
                "approval_status": "approved"
            }
            result = self.graph.execute_contract_approval(
                contract_type="PURCHASE",
                contract_id="CON001",
                amount=50000.0
            )
            assert result is not None
    
    def test_contract_type_outsource(self):
        """测试外包合同审批流程"""
        with patch.object(self.graph, 'execute', new_callable=AsyncMock):
            result = self.graph.execute_contract_approval(
                contract_type="OUTSOURCE",
                contract_id="CON002",
                amount=30000.0
            )
            assert result is not None
    
    def test_contract_type_framework(self):
        """测试框架协议审批流程"""
        with patch.object(self.graph, 'execute', new_callable=AsyncMock):
            result = self.graph.execute_contract_approval(
                contract_type="FRAMEWORK",
                contract_id="CON003",
                amount=100000.0
            )
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_execute_with_initial_state(self):
        """测试带初始状态的执行"""
        with patch.object(self.graph, 'nodes', {}):
            self.graph.nodes['ENTRY'] = MagicMock()
            self.graph.nodes['EXIT'] = MagicMock()
            result = await self.graph.execute({"custom_field": "test"})
            assert result.get("custom_field") == "test"
    
    @pytest.mark.asyncio
    async def test_validation(self):
        """测试图验证"""
        assert self.graph.validate() is True


@pytest.mark.asyncio
async def test_demo_contract_approval_v2():
    """测试演示函数"""
    with patch('irp.masfactory.examples.contract_approval_v2.ContractApprovalGraph'):
        result = await demo_contract_approval_v2()
        assert result is not None

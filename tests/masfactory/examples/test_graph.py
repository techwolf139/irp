"""核心组件测试 - Graph/Loop/Agent/State"""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from irp.mas_factory.core.graph import Graph, Edge
from irp.mas_factory.core.loop import Loop
from irp.mas_factory.core.agent import Agent, AgentDefinition
from irp.mas_factory.core.state import State


class TestGraph:
    """测试 Graph 组件"""
    
    def setup_method(self):
        """每个测试前的准备"""
        self.graph = Graph(name="test_graph")
    
    def test_create_node(self):
        """测试创建节点"""
        agent_def = AgentDefinition(name="test_agent", description="测试助手")
        agent = Agent(name="test_node", agent_def=agent_def)
        
        self.graph.create_node("node_1", agent)
        assert "node_1" in self.graph.nodes
    
    def test_create_edge(self):
        """测试创建边"""
        self.graph.create_edge("node_1", "node_2")
        assert len(self.graph.edges) == 1
    
    def test_validate(self):
        """测试验证"""
        # 空图应该验证失败
        assert self.graph.validate() is False
        
        # 有边但无节点
        self.graph.create_edge("node_1", "node_2")
        assert self.graph.validate() is False
        
        # 有节点无边
        graph2 = Graph(name="graph2")
        agent = Agent(name="test_node", agent_def=AgentDefinition(name="test", description="test"))
        graph2.create_node("node_1", agent)
        assert graph2.validate() is False
    
    @pytest.mark.asyncio
    async def test_execute_empty(self):
        """测试空图执行"""
        result = await self.graph.execute({"test": "data"})
        assert result == {"test": "data"}
    
    def test_to_dict(self):
        """测试转换为字典"""
        agent_def = AgentDefinition(name="test_agent", description="测试助手")
        agent = Agent(name="test_node", agent_def=agent_def)
        
        self.graph.create_node("node_1", agent)
        
        result = self.graph.to_dict()
        
        assert "node_1" in result.get("nodes", [])
        assert len(result.get("metadata", {})) > 0


class TestAgent:
    """测试 Agent 组件"""
    
    def test_agent_initialization(self):
        """测试 Agent 初始化"""
        agent_def = AgentDefinition(
            name="test_agent",
            description="测试助手",
            skills=["测试技能"]
        )
        agent = Agent(name="test", agent_def=agent_def)
        
        assert agent.name == "test"
        assert agent.agent_def.name == "test_agent"
        assert "测试技能" in agent.agent_def.skills
    
    def test_agent_validate(self):
        """测试 Agent 验证"""
        agent_def = AgentDefinition(name="test", description="测试")
        agent = Agent(name="test", agent_def=agent_def)
        assert agent.validate() is True
        
        # 无效 Agent
        invalid_def = AgentDefinition(name="", description="")
        invalid_agent = Agent(name="test", agent_def=invalid_def)
        assert invalid_agent.validate() is False
    
    @pytest.mark.asyncio
    async def test_agent_execute(self):
        """测试 Agent 执行"""
        agent_def = AgentDefinition(name="test_agent", description="测试助手")
        agent = Agent(name="test", agent_def=agent_def)
        
        state = State(data={"input": "test"})
        result = await agent.execute(state)
        
        assert isinstance(result, dict)
        assert "result" in result


class TestState:
    """测试 State 组件"""
    
    def test_get_set(self):
        """测试读写状态"""
        state = State()
        state.set("key", "value")
        assert state.get("key") == "value"
    
    def test_update(self):
        """测试批量更新"""
        state = State()
        state.update(a=1, b=2, c=3)
        
        assert state.get("a") == 1
        assert state.get("b") == 2
        assert state.get("c") == 3
    
    def test_node_history(self):
        """测试节点历史"""
        state = State()
        state.node_visited("node_1")
        state.node_visited("node_2")
        
        assert "node_1" in state.node_history
        assert "node_2" in state.node_history
    
    def test_copy(self):
        """测试深拷贝"""
        state = State(data={"key": "value"})
        copied = state.copy()
        
        assert copied.get("key") == "value"
        assert copied is not state


@pytest.mark.asyncio
async def test_loop_execution():
    """测试 Loop 执行"""
    # 简化测试
    graph = Graph(name="inner_graph")
    agent_def = AgentDefinition(name="test", description="test")
    agent = Agent(name="node_1", agent_def=agent_def)
    graph.create_node("node_1", agent)
    
    loop = Loop(
        name="test_loop",
        inner_graph=graph,
        max_iterations=3
    )
    
    assert loop.validate() is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

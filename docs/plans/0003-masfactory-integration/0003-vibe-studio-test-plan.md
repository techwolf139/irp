# VibeGraph Studio 测试计划

**日期**: 2026-04-05  
**范围**: 前端 + 后端集成测试  
**优先级**: High

---

## 🎯 测试目标

验证 VibeGraph Studio 前后端功能的正确性、稳定性和性能：

1. **前端组件测试** - React 组件功能正确性
2. **后端 API 集成** - VibeGraph API 正确调用
3. **状态管理** - React context + hooks 功能
4. **错误处理** - 异常场景下的系统行为
5. **性能测试** - 加载时间和响应时间

---

## 🧪 测试范围

### 前端测试 (VibeStudio)

| 测试类别 | 文件 | 测试点 |
|---------|-----|------|
| **GraphUtils** | graphUtils.ts | 节点/边创建、验证、拓扑排序 |
| **VibeGraph** | useVibeGraph.ts | API 调用、状态管理、错误处理 |
| **VibeInput** | VibeInput.tsx | 表单验证、提交逻辑 |
| **GraphEditor** | GraphEditor.tsx | ReactFlow 集成、节点操作 |
| **NodePanel** | NodePanel.tsx | 节点点击、状态管理 |
| **DesignPreview** | DesignPreview.tsx | 数据展示、更新 |
| **App Integration** | App.tsx | 组件组合、状态传递 |

### 后端测试 (Python)

| 测试类别 | 模块 | 测试点 |
|---------|-----|------|
| **Graph Engine** | core/graph.py | 节点创建、边连接、拓扑排序 |
| **Loop** | core/loop.py | 循环执行、终止条件 |
| **Agent** | core/agent.py | 执行生命周期、状态传递 |
| **State** | core/state.py | 读写、历史追踪 |
| **VibeGraph** | vibe/ | 三阶段生成、缓存保存 |
| **Stage Components** | stage_components.py | 角色分配、拓扑设计、语义补全 |
| **DesignCache** | cache.py | 缓存读写、元数据管理 |
| **VibeApi** | vibe_approval_api.py | FastAPI 端点、请求验证 |

---

## 📋 测试用例清单

### Phase 1: 前端单元测试 (Jest + React Testing Library)

#### 1.1 GraphUtils 测试

**测试文件**: `tests/masfactory/examples/vite-studio/graphUtils.test.ts`

```typescript
describe('GraphUtils', () => {
  describe('createEmptyGraph', () => {
    it('should create graph with ENTRY and EXIT nodes', () => {
      const graph = createEmptyGraph('Test intent');
      expect(graph.nodes.length).toBe(2);
      expect(graph.nodes[0].id).toBe('entry');
      expect(graph.nodes[1].id).toBe('exit');
    });
    
    it('should assign correct metadata', () => {
      const graph = createEmptyGraph('Test intent');
      expect(graph.metadata.user_intent).toBe('Test intent');
      expect(graph.metadata.role_count).toBe(0);
      expect(graph.metadata.node_count).toBe(2);
    });
  });
  
  describe('createAgentNode', () => {
    it('should create valid agent node', () => {
      const node = createAgentNode('node_1', 'Approver', 'Approver Role');
      expect(node.type).toBe('Agent');
      expect(node.data.role).toBe('Approver');
      expect(node.data.title).toBe('Approver Role');
    });
  });
  
  describe('addNode', () => {
    it('should add node and increment count', () => {
      let graph = createEmptyGraph('Test');
      const newNode = createAgentNode('node_2', 'Approver', 'Approver Role');
      graph = addNode(graph, newNode);
      expect(graph.nodes.length).toBe(3);
      expect(graph.metadata.node_count).toBe(3);
    });
  });
  
  describe('validateGraph', () => {
    it('should validate complete graph', () => {
      const graph = {
        metadata: { user_intent: 'Test', role_count: 1, node_count: 2, created_at: Date.now().toString(), design_version: '1.0' },
        nodes: [
          { id: 'entry', type: 'Entry', position: { x: 0, y: 0 }, data: { title: 'Entry', instructions: '', inputFields: [], outputFields: [], tools: [] } },
          { id: 'exit', type: 'Exit', position: { x: 0, y: 0 }, data: { title: 'Exit', instructions: '', inputFields: [], outputFields: [], tools: [] } }
        ],
        edges: [{ id: 'e1', source: 'entry', target: 'exit' }]
      };
      const result = validateGraph(graph);
      expect(result.isValid).toBe(true);
    });
    
    it('should detect validation errors', () => {
      const graph = {
        metadata: { user_intent: 'Test', role_count: 0, node_count: 1, created_at: Date.now().toString(), design_version: '1.0' },
        nodes: [
          { id: 'node_1', type: 'Agent', position: { x: 0, y: 0 }, data: { title: '', instructions: '', inputFields: [], outputFields: [], tools: [] } }
        ],
        edges: []
      };
      const result = validateGraph(graph);
      expect(result.isValid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
    });
  });
});
```

#### 1.2 VibeGraph hook 测试

**测试文件**: `tests/masfactory/examples/vite-studio/useVibeGraph.test.tsx`

```typescript
import { renderHook, act } from '@testing-library/react';
import { useVibeGraph } from '../../src/hooks/useVibeGraph';
import { mockFetch } from '../mocks/mockFetch';

describe('useVibeGraph', () => {
  const originalFetch = global.fetch;
  
  beforeEach(() => {
    global.fetch = mockFetch;
    localStorage.clear();
  });
  
  afterEach(() => {
    global.fetch = originalFetch;
  });
  
  it('should initialize with empty state', () => {
    const { result } = renderHook(() => useVibeGraph());
    expect(result.current.state.user_intent).toBe('');
    expect(result.current.state.node_count).toBe(0);
    expect(result.current.state.is_generating).toBe(false);
  });
  
  it('should generate graph successfully', async () => {
    const { result } = renderHook(() => useVibeGraph());
    
    await act(async () => {
      await result.current.generateGraph({
        user_intent: 'Create procurement contract approval workflow'
      });
    });
    
    expect(result.current.state.user_intent).toBe('Create procurement contract approval workflow');
    expect(result.current.state.node_count).toBeGreaterThan(0);
    expect(result.current.state.is_generating).toBe(false);
  });
  
  it('should handle generation errors', async () => {
    global.fetch = mockFetch({
      ok: false,
      status: 500,
      data: { error: 'Server error' }
    });
    
    const { result } = renderHook(() => useVibeGraph());
    const originalConsoleError = console.error;
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    
    await act(async () => {
      try {
        await result.current.generateGraph({
          user_intent: 'Test intent'
        });
      } catch (e) {
        // Expected to throw
        expect(e).toBeTruthy();
      }
    });
    
    expect(consoleErrorSpy).toHaveBeenCalled();
    consoleErrorSpy.mockRestore();
  });
  
  it('should reset state correctly', () => {
    const { result } = renderHook(() => useVibeGraph());
    
    act(() => {
      result.current.generateGraph({ user_intent: 'Test' });
    });
    
    expect(result.current.state.user_intent).toBe('Test');
    
    act(() => {
      result.current.reset();
    });
    
    expect(result.current.state.user_intent).toBe('');
    expect(result.current.state.node_count).toBe(0);
  });
});
```

#### 1.3 VibeInput 组件测试

**测试文件**: `tests/masfactory/examples/vite-studio/components/VibeInput.test.tsx`

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { VibeInput } from '../../../../src/components/VibeInput';

const mockOnGenerate = vi.fn();

describe('VibeInput', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });
  
  it('should render VibeInput component', () => {
    render(<VibeInput onGenerate={mockOnGenerate} isGenerating={false} />);
    expect(screen.getByText('VibeGraph 生成')).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/工作流程描述/)).toBeInTheDocument();
  });
  
  it('should have workflow template input', () => {
    render(<VibeInput onGenerate={mockOnGenerate} isGenerating={false} />);
    expect(screen.getByPlaceholderText(/具体需求/)).toBeInTheDocument();
  });
    
  it('should disable generate button when empty', () => {
    render(<VibeInput onGenerate={mockOnGenerate} isGenerating={false} />);
    const button = screen.getByRole('button', { name: /生成 VibeGraph/i });
    expect(button).toBeDisabled();
  });
  
  it('should enable generate button when filled', async () => {
    render(<VibeInput onGenerate={mockOnGenerate} isGenerating={false} />);
    const input = screen.getByRole('textbox', { name: /具体需求/ });
    fireEvent.change(input, { target: { value: 'START->A,B,C->D->END' } });
    const button = screen.getByRole('button', { name: /生成 VibeGraph/i });
    await waitFor(() => {
      expect(button).not.toBeDisabled();
    });
  });
  
  it('should call onGenerate on form submit', async () => {
    render(<VibeInput onGenerate={mockOnGenerate} isGenerating={false} />);
    const input = screen.getByRole('textbox', { name: /具体需求/ });
    fireEvent.change(input, { target: { value: 'Test workflow' } });
    const button = screen.getByRole('button', { name: /生成 VibeGraph/i });
    fireEvent.click(button);
    await waitFor(() => {
      expect(mockOnGenerate).toHaveBeenCalledWith('Test workflow');
    });
  });
  
  it('should show loading state when generating', () => {
    render(<VibeInput onGenerate={mockOnGenerate} isGenerating={true} />);
    const button = screen.getByRole('button', { name: /生成中.../i });
    expect(button).toBeDisabled();
  });
  
  it('should display tips section', () => {
    render(<VibeInput onGenerate={mockOnGenerate} isGenerating={false} />);
    expect(screen.getByText(/使用技巧/)).toBeInTheDocument();
    expect(screen.getByText(/\d+\. 支持描述/)).toBeInTheDocument();
  });
});
```

#### 1.4 其他组件测试

**测试文件**: `tests/masfactory/examples/vite-studio/components/GraphEditor.test.tsx`
```typescript
import { render } from '@testing-library/react';
import { GraphEditor } from '../../../../src/components/GraphEditor';

describe('GraphEditor', () => {
  it('should show empty state when no nodes', () => {
    const { getByText } = render(<GraphEditor nodes={[]} edges={[]} />);
    expect(getByText(/请先生成 VibeGraph/)).toBeInTheDocument();
  });
});
```

---

### Phase 2: 后端单元测试 (pytest)

#### 2.1 GraphCore 测试

**测试文件**: `tests/masfactory/test_graph_core.py`

```python
import pytest
from irp.mas_factory.core.graph import Graph, Edge
from irp.mas_factory.core.node import Node
from irp.mas_factory.core.agent import Agent, AgentDefinition


class TestGraphCore:
    
    def test_create_node(self):
        graph = Graph(name="test")
        agent_def = AgentDefinition(name="test_agent", description="Test")
        agent = Agent(name="test_node", agent_def=agent_def)
        graph.create_node("node_1", agent)
        
        assert "node_1" in graph.nodes
        assert len(graph.nodes) == 1
    
    def test_create_edge(self):
        graph = Graph(name="test")
        graph.create_edge("node_1", "node_2")
        
        assert len(graph.edges) == 1
        assert graph.edges[0].source == "node_1"
        assert graph.edges[0].target == "node_2"
    
    def test_validate_with_nodes_and_edges(self):
        graph = Graph(name="test")
        agent_def = AgentDefinition(name="test", description="test")
        agent = Agent(name="node_1", agent_def=agent_def)
        graph.create_node("node_1", agent)
        graph.create_edge("node_1", "node_2")
        
        assert graph.validate() is True
    
    def test_validate_without_nodes(self):
        graph = Graph(name="test")
        assert graph.validate() is False
    
    def test_validate_without_edges(self):
        graph = Graph(name="test")
        agent = Agent(name="test", agent_def=AgentDefinition(name="test", description="test"))
        graph.create_node("node_1", agent)
        assert graph.validate() is False
    
    @pytest.mark.asyncio
    async def test_execute_empty_graph(self):
        graph = Graph(name="test")
        result = await graph.execute({"test_key": "test_value"})
        assert result == {"test_key": "test_value"}
    
    def test_to_dict(self):
        graph = Graph(name="test")
        agent = Agent(name="test", agent_def=AgentDefinition(name="test", description="test"))
        graph.create_node("node_1", agent)
        graph.create_edge("node_1", "node_2")
        
        result = graph.to_dict()
        
        assert "test" in result.get("name", "")
        assert "node_1" in result.get("nodes", [])
        assert len(result.get("edges", [])) > 0
```

#### 2.2 AgentCore 测试

**测试文件**: `tests/masfactory/test_agent_core.py`

```python
import pytest
from irp.mas_factory.core.agent import Agent, AgentDefinition


class TestAgentCore:
    
    def test_agent_initialization(self):
        agent_def = AgentDefinition(
            name="test_agent",
            description="Test助手",
            skills=["测试技能"]
        )
        agent = Agent(name="test", agent_def=agent_def)
        
        assert agent.name == "test"
        assert agent.agent_def.name == "test_agent"
        assert "测试技能" in agent.agent_def.skills
    
    def test_agent_validate_valid(self):
        agent_def = AgentDefinition(name="test_agent", description="Test")
        agent = Agent(name="test", agent_def=agent_def)
        assert agent.validate() is True
    
    def test_agent_validate_invalid_name(self):
        agent_def = AgentDefinition(name="", description="Test")
        agent = Agent(name="test", agent_def=agent_def)
        assert agent.validate() is False
    
    def test_agent_validate_invalid_description(self):
        agent_def = AgentDefinition(name="test", description="")
        agent = Agent(name="test", agent_def=agent_def)
        assert agent.validate() is False
    
    @pytest.mark.asyncio
    async def test_agent_execute_structure(self):
        from irp.mas_factory.core.state import State
        
        agent_def = AgentDefinition(name="test_agent", description="Test")
        agent = Agent(name="test", agent_def=agent_def)
        
        state = State(data={"test_input": "data"})
        result = await agent.execute(state)
        
        assert isinstance(result, dict)
        assert "result" in result
        assert "Processed:" in result["result"]
```

#### 2.3 StageComponents 测试

**测试文件**: `tests/masfactory/test_stage_components.py`

```python
import pytest
from irp.mas_factory.vibe.stage_components import (
    RoleAssigner,
    TopologyDesigner,
    SemanticCompleter,
    VibeGraphStages
)


class TestRoleAssigner:
    
    def test_assign_roles_approval_pattern(self):
        assigner = RoleAssigner()
        roles = assigner.assign_roles("采购审批流程")
        
        assert len(roles) > 0
        roles_str = [r.get("role") for r in roles]
        assert any("审批" in r for r in roles_str) or len(roles_str) > 0
    
    def test_assign_roles_default(self):
        assigner = RoleAssigner()
        roles = assigner.assign_roles("未知需求")
        
        assert len(roles) > 0
        assert roles[0].get("role") in ["通用智能体", "advisor"]
    
    def test_assign_roles_invalid_pattern(self):
        assigner = RoleAssigner()
        roles = assigner.assign_roles("test")
        
        assert len(roles) >= 1
    
    def test_validate_roles_valid(self):
        assigner = RoleAssigner()
        roles = [
            {"name": "测试角色", "role": "test_role", "skills": ["技能 1"]}
        ]
        assert assigner.validate_roles(roles) is True
    
    def test_validate_roles_invalid(self):
        assigner = RoleAssigner()
        assert assigner.validate_roles([]) is False
        
        assigner = RoleAssigner()
        invalid_roles = [{"name": "", "role": "test"}]
        assert assigner.validate_roles(invalid_roles) is False


class TestTopologyDesigner:
    
    def test_design_topology(self):
        designer = TopologyDesigner()
        roles = [
            {"role": "approver", "name": "审批员"},
            {"role": "legal", "name": "法务"}
        ]
        
        topology = designer.design_topology(roles)
        
        assert "nodes" in topology
        assert "edges" in topology
        assert topology["metadata"]["type"] == "linear_graph"
    
    def test_topology_contains_entry_exit(self):
        designer = TopologyDesigner()
        topology = designer.design_topology([{"role": "test"}])
        
        edge_sources = [e["source"] for e in topology["edges"]]
        edge_targets = [e["target"] for e in topology["edges"]]
        
        assert "ENTRY" in edge_sources
        assert "EXIT" in edge_targets
    
    def test_validate_topology(self):
        designer = TopologyDesigner()
        topology = designer.design_topology([{"role": "test"}])
        assert designer.validate_topology(topology) is True
    
    def test_validate_topology_invalid(self):
        designer = TopologyDesigner()
        assert designer.validate_topology({}) is False
        
        invalid_topology = {
            "nodes": [{"id": "node_1"}],
            "edges": [{"source": "node_1", "target": "node_2"}]
        }
        assert designer.validate_topology(invalid_topology) is False


class TestSemanticCompleter:
    
    def test_complete_semantics(self):
        completer = SemanticCompleter()
        topology = {
            "nodes": [{"id": "node_1", "role": "agent"}],
            "edges": [{"source": "ENTRY", "target": "node_1"}],
            "metadata": {"type": "test"}
        }
        roles = [{"role": "approver", "name": "审批员"}]
        
        result = completer.complete_semantics(topology, roles, "test intent")
        
        assert "nodes" in result
        assert len(result["nodes"]) > 0
        assert "instructions" in result["nodes"][0]


class TestVibeGraphStages:
    
    @pytest.mark.asyncio
    async def test_execute_pipeline(self):
        stages = VibeGraphStages()
        result = await stages.execute_pipeline("采购合同审批流程")
        
        assert "nodes" in result
        assert "edges" in result
        assert result["metadata"]["user_intent"] == "采购合同审批流程"
```

---

### Phase 3: 集成测试

#### 3.1 Frontend + Backend API 集成

**测试文件**: `tests/masfactory/examples/vite-studio/integration.test.ts`

```typescript
import { describe, it, expect, beforeEach, vi } from 'vitest';
import axios from 'axios';
import { vibeGraphApi } from '../../../../src/api/axiosConfig';
import { mockFetch } from '../mocks/mockFetch';

describe('VibeGraph API Integration', () => {
  const originalFetch = global.fetch;
  
  beforeEach(() => {
    global.fetch = mockFetch;
  });
  
  afterEach(() => {
    global.fetch = originalFetch;
  });
  
  describe('generate', () => {
    it('should generate graph from API', async () => {
      const mockResponse = {
        config: {
          nodes: [
            { id: 'node_1', type: 'agent' },
            { id: 'node_2', type: 'agent' }
          ],
          edges: [
            { source: 'entry', target: 'node_1' },
            { source: 'node_1', target: 'node_2' },
            { source: 'node_2', target: 'exit' }
          ]
        },
        metadata: {
          nodes_count: 2,
          edges_count: 3,
          roles: [{ role: 'approver' }]
        }
      };
      
      global.fetch = mockFetch({ ok: true, json: mockResponse });
      
      const result = await vibeGraphApi.generate({
        user_intent: 'Test workflow',
        topology_type: 'linear'
      });
      
      expect(result).toEqual(mockResponse);
      expect(result.config.nodes.length).toBe(2);
      expect(result.config.edges.length).toBe(3);
    });
    
    it('should handle API errors', async () => {
      global.fetch = mockFetch({ ok: false, status: 500, json: { error: 'Server error' } });
      
      await expect(
        vibeGraphApi.generate({
          user_intent: 'Test workflow'
        })
      ).rejects.toThrow();
    });
  });
  
  describe('preview', () => {
    it('should get design preview', async () => {
      const mockDesign = {
        nodes: [{ id: 'node_1' }, { id: 'node_2' }],
        edges: [{ source: 'node_1', target: 'node_2' }],
        metadata: { type: 'linear', node_count: 2, edge_count: 1 }
      };
      
      global.fetch = mockFetch({ ok: true, json: mockDesign });
      
      const result = await vibeGraphApi.preview('design_123');
      expect(result).toEqual(mockDesign);
    });
  });
  
  describe('execute', () => {
    it('should execute graph', async () => {
      const mockExecutionResult = {
        graph_id: 'test_graph',
        status: 'completed',
        result: { data: 'execution output' },
        execution_time: 123
      };
      
      global.fetch = mockFetch({ ok: true, json: mockExecutionResult });
      
      const result = await vibeGraphApi.execute('test_graph', {});
      expect(result).toEqual(mockExecutionResult);
      expect(result.status).toBe('completed');
    });
    
    it('should fail execution with invalid graph', async () => {
      global.fetch = mockFetch({ 
        ok: false, 
        status: 400,
        json: { error: 'Invalid graph ID' }
      });
      
      await expect(
        vibeGraphApi.execute('invalid_graph_id', {})
      ).rejects.toThrow('Invalid graph ID');
    });
  });
});
```

#### 3.2 Python Backend Integration

**测试文件**: `tests/masfactory/test_backend_integration.py`

```python
import pytest
from fastapi.testclient import TestClient
from irp.api.vibe_approval_api import app


@pytest.fixture
def client():
    return TestClient(app)


class TestVibeApprovalAPI:
    
    def test_health_check(self, client: TestClient):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "running"
        assert "timestamp" in data
    
    def test_root_endpoint(self, client: TestClient):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
    
    def test_get_approval_types(self, client: TestClient):
        response = client.get("/api/v1/approval/types")
        assert response.status_code == 200
        data = response.json()
        assert "approved_types" in data
        assert len(data["approved_types"]) == 3
        assert data["vibe_graphing_support"] is True
    
    def test_approve_contract_v1_validation(self, client: TestClient):
        response = client.post(
            "/api/v1/contracts/test_contract/approval/v1",
            json={
                "contract_id": "TEST001",
                "contract_type": "INVALID_TYPE",
                "amount": -100
            }
        )
        # Should fail validation
        assert response.status_code in [400, 422]
    
    def test_approve_contract_vibe(self, client: TestClient):
        response = client.post(
            "/api/v1/contracts/test_contract/approval/vibe",
            json={
                "contract_id": "CON2024001",
                "contract_type": "PURCHASE",
                "amount": 100000.0,
                "title": "Test procurement"
            }
        )
        assert response.status_code == 200
```

---

### Phase 4: 错误场景测试

#### 4.1 网络错误处理

**测试文件**: `tests/masfactory/examples/vite-studio/error-handling.test.ts`

```typescript
import { renderHook } from '@testing-library/react';
import { useVibeGraph } from '../../../../src/hooks/useVibeGraph';

describe('Error Handling', () => {
  it('should handle network errors gracefully', async () => {
    const originalFetch = global.fetch;
    global.fetch = () => Promise.reject(new Error('Network error'));
    
    const { result } = renderHook(() => useVibeGraph());
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    
    await expect(
      result.current.generateGraph({ user_intent: 'Test' })
    ).rejects.toThrow();
    
    expect(consoleErrorSpy).toHaveBeenCalled();
    consoleErrorSpy.mockRestore();
    global.fetch = originalFetch;
  });
  
  it('should show loading state then fail on timeout', async () => {
    const originalFetch = global.fetch;
    setTimeout(() => {
      global.fetch = () => Promise.reject(new Error('Timeout'));
    }, 0);
    
    global.fetch = () => new Promise(() => {}); // Never resolves
    
    const { result } = renderHook(() => useVibeGraph());
    const startGenerating = () => result.current.generateGraph({ user_intent: 'Test' });
    
    await startGenerating();
    expect(result.current.state.is_generating).toBe(true);
    
    // Wait for timeout
    await new Promise(resolve => setTimeout(resolve, 5000));
    global.fetch = originalFetch;
  });
});
```

---

### Phase 5: 性能测试

#### 5.1 加载性能

**测试文件**: `tests/masfactory/examples/vite-studio/performance.test.ts`

```typescript
import { renderHook } from '@testing-library/react';
import { useVibeGraph } from '../../../../src/hooks/useVibeGraph';

describe('Performance Tests', () => {
  afterEach(() => {
    vi.useRealTimers();
  });
  
  it('should generate graph within acceptable time', async () => {
    const { result } = renderHook(() => useVibeGraph());
    
    const startTime = Date.now();
    await result.current.generateGraph({
      user_intent: 'Test workflow with multiple nodes'
    });
    const executionTime = Date.now() - startTime;
    
    // Should complete within 500ms for simple graph
    expect(executionTime).toBeLessThan(1000);
    expect(executionTime).toBeGreaterThanOrEqual(0);
  });
  
  it('should not block UI during operation', async () => {
    const { result } = renderHook(() => useVibeGraph());
    const uiBlockSpy = vi.fn();
    
    await result.current.generateGraph({
      user_intent: 'Heavy operation'
    });
    
    expect(uiBlockSpy).not.toHaveBeenCalled();
  });
});
```

---

## 📐 测试覆盖率目标

| 模块 | 当前 | 目标 |
|-----|-----|-----|
| **GraphUtils** | -% | 90% |
| **VibeGraph Hook** | -% | 85% |
| **VibeInput Component** | -% | 90% |
| **GraphEditor Component** | -% | 80% |
| **NodePanel Component** | -% | 85% |
| **DesignPreview Component** | -% | 80% |
| **Python Core Modules** | 76% | 90% |
| **Vibe API Integration** | -% | 90% |

**总体目标:** >85% 覆盖率

---

## 🚀 执行顺序

1. **安装依赖**: `npm install && cd ..`
2. **安装测试运行器**: `npm install --save-dev vitest @testing-library/react @testing-library/jest-dom vitest-environment-jsdom`
3. **运行前端测试**: `npm test -- --coverage`
4. **运行后端测试**: `cd .. && pytest tests/masfactory/ -v --cov=irp`
5. **集成测试**: `npm run test:integration`

---

*计划创建时间：2026-04-05*  
*VibeGraph Studio Test Plan*

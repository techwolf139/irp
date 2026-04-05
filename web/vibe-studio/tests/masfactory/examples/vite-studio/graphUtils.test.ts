/**
 * Graph Utils 测试
 * 测试图数据结构的创建、验证、修改功能
 */

import { describe, it, expect } from 'vitest';
import {
  createEmptyGraph,
  createEntryAndExitNodes,
  createAgentNode,
  addNode,
  addEdge,
  validateGraph,
  detectCyclicEdges
} from '../../src/api/graphUtils';

describe('GraphUtils', () => {
  describe('createEmptyGraph', () => {
    it('should create graph with ENTRY and EXIT nodes', () => {
      const graph = createEmptyGraph('Test workflow');
      expect(graph.nodes.length).toBe(2);
      expect(graph.nodes[0].id).toBe('entry');
      expect(graph.nodes[0].type).toBe('Entry');
      expect(graph.nodes[1].id).toBe('exit');
      expect(graph.nodes[1].type).toBe('Exit');
    });

    it('should assign correct metadata', () => {
      const graph = createEmptyGraph('Import workflow');
      expect(graph.metadata.user_intent).toBe('Import workflow');
      expect(graph.metadata.role_count).toBe(0);
      expect(graph.metadata.node_count).toBe(2);
      expect(graph.metadata.design_version).toBe('1.0.0');
      expect(new Date(graph.metadata.created_at).toISOString()).toBeDefined();
    });

    it('should initialize with empty nodes metadata', () => {
      const graph = createEmptyGraph('');
      expect(graph.metadata.user_intent).toBe('');
    });
  });

  describe('createEntryAndExitNodes', () => {
    it('should create exactly 2 nodes', () => {
      const nodes = createEntryAndExitNodes();
      expect(nodes.length).toBe(2);
    });

    it('should name nodes entry and exit', () => {
      const nodes = createEntryAndExitNodes();
      const ids = nodes.map(n => n.id);
      expect(ids).toContain('entry');
      expect(ids).toContain('exit');
    });

    it('should have correct types', () => {
      const nodes = createEntryAndExitNodes();
      expect(nodes[0].type).toBe('Entry');
      expect(nodes[1].type).toBe('Exit');
    });

    it('should have expected positions', () => {
      const nodes = createEntryAndExitNodes();
      expect(nodes[0].position.x).toBe(100);
      expect(nodes[0].position.y).toBe(300);
      expect(nodes[1].position.x).toBe(600);
      expect(nodes[1].position.y).toBe(300);
    });
  });

  describe('createAgentNode', () => {
    it('should create valid agent node with correct ID', () => {
      const node = createAgentNode('agent_1', 'Approver', 'Approval Role');
      expect(node.id).toBe('agent_1');
      expect(node.type).toBe('Agent');
    });

    it('should set correct role information', () => {
      const node = createAgentNode('reviewer', 'Reviewer', 'Review');
      expect(node.data.role).toBe('Reviewer');
      expect(node.data.title).toBe('Review');
    });

    it('should initialize with empty fields', () => {
      const node = createAgentNode('test', 'Test', 'Test Role');
      expect(node.data.instructions).toBe('');
      expect(node.data.inputFields).toEqual([]);
      expect(node.data.outputFields).toEqual([]);
      expect(node.data.tools).toEqual([]);
      expect(node.data.status).toBe('pending');
    });
  });

  describe('addNode', () => {
    it('should add node to graph', () => {
      const graph = createEmptyGraph('Test');
      const newNode = createAgentNode('node_2', 'Approver', 'Test Role');
      const updated = addNode(graph, newNode);
      
      expect(updated.nodes.length).toBe(3);
      expect(updated.metadata.node_count).toBe(3);
    });

    it('should not duplicate existing nodes', () => {
      const graph = createEmptyGraph('Test');
      const newNode = createAgentNode('entry', 'Approver', 'Test');
      const updated = addNode(graph, newNode);
      
      expect(updated.nodes.length).toBe(3);
      const entryNodes = updated.nodes.filter(n => n.id === 'entry');
      expect(entryNodes.length).toBe(1);
    });

    it('should preserve original graph structure', () => {
      const graph = createEmptyGraph('Test');
      const newNode = createAgentNode(
        'node_2',
        'Approver',
        'Test Role'
      );
      const updated = addNode(graph, newNode);
      
      expect(updated.metadata.user_intent).toBe('Test');
      expect(updated.metadata.role_count).toBe(0);
    });

    it('should handle multiple node additions', () => {
      let graph = createEmptyGraph('Test');
      const nodes = [
        createAgentNode('n1', 'A1', 'Role1'),
        createAgentNode('n2', 'A2', 'Role2'),
        createAgentNode('n3', 'A3', 'Role3')
      ];
      
      for (const node of nodes) {
        graph = addNode(graph, node);
      }
      
      expect(graph.nodes.length).toBe(5);
      expect(graph.metadata.node_count).toBe(5);
    });
  });

  describe('addEdge', () => {
    it('should add edge to graph', () => {
      const graph = createEmptyGraph('Test');
      const newEdge = {
        id: 'edge_1',
        source: 'entry',
        target: 'exit',
        animated: false
      };
      const updated = addEdge(graph, newEdge);
      
      expect(updated.edges.length).toBe(1);
      expect(updated.edges[0].id).toBe('edge_1');
    });

    it('should preserve existing structure', () => {
      const graph = createEmptyGraph('Test');
      graph = addNode(graph, createAgentNode('n1', 'A1', 'Role'));
      
      const newEdge = {
        id: 'edge_1',
        source: 'entry',
        target: 'n1'
      };
      const updated = addEdge(graph, newEdge);
      
      expect(updated.nodes.length).toBe(3);
      expect(updated.edges.length).toBe(1);
    });

    it('should allow multiple edges', () => {
      const graph = createEmptyGraph('Test');
      const edges = [
        { id: 'e1', source: 'entry', target: 'n1' },
        { id: 'e2', source: 'n1', target: 'n2' },
        { id: 'e3', source: 'n2', target: 'exit' }
      ];
      
      let result = graph;
      for (const edge of edges) {
        result = addEdge(result, edge);
      }
      
      expect(result.edges.length).toBe(3);
    });
  });

  describe('validateGraph', () => {
    it('should validate complete valid graph', () => {
      const validGraph = {
        metadata: {
          user_intent: 'Test',
          role_count: 1,
          node_count: 3,
          created_at: new Date().toISOString(),
          design_version: '1.0.0'
        },
        nodes: [
          {
            id: 'entry',
            type: 'Entry',
            position: { x: 0, y: 0 },
            data: {
              title: 'Entry',
              instructions: 'Start',
              inputFields: [],
              outputFields: [],
              tools: []
            }
          },
          {
            id: 'node1',
            type: 'Agent',
            position: { x: 100, y: 100 },
            data: {
              title: 'Agent1',
              instructions: 'Process',
              inputFields: ['in1'],
              outputFields: ['out1'],
              tools: ['tool1']
            }
          },
          {
            id: 'exit',
            type: 'Exit',
            position: { x: 200, y: 200 },
            data: {
              title: 'Exit',
              instructions: 'End',
              inputFields: [],
              outputFields: [],
              tools: []
            }
          }
        ],
        edges: [
          { id: 'e1', source: 'entry', target: 'node1', animated: false },
          { id: 'e2', source: 'node1', target: 'exit', animated: true }
        ]
      };
      
      const result = validateGraph(validGraph);
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
      expect(result.warnings).toHaveLength(0);
    });

    it('should detect missing title', () => {
      const invalidGraph = {
        metadata: {
          user_intent: 'Test',
          role_count: 0,
          node_count: 2,
          created_at: new Date().toISOString(),
          design_version: '1.0.0'
        },
        nodes: [
          {
            id: 'entry',
            type: 'Entry',
            position: { x: 0, y: 0 },
            data: {
              title: '',
              instructions: '',
              inputFields: [],
              outputFields: [],
              tools: []
            }
          },
          {
            id: 'exit',
            type: 'Exit',
            position: { x: 0, y: 0 },
            data: {
              title: 'Exit',
              instructions: '',
              inputFields: [],
              outputFields: [],
              tools: []
            }
          }
        ],
        edges: [{ id: 'e1', source: 'entry', target: 'exit' }]
      };
      
      const result = validateGraph(invalidGraph);
      expect(result.isValid).toBe(false);
      expect(result.errors.length).toBe(1);
      expect(result.errors[0]).toContain('title');
    });

    it('should detect missing instructions (warning)', () => {
      const graph = {
        metadata: {
          user_intent: 'Test',
          role_count: 0,
          node_count: 2,
          created_at: new Date().toISOString(),
          design_version: '1.0.0'
        },
        nodes: [
          {
            id: 'entry',
            type: 'Entry',
            position: { x: 0, y: 0 },
            data: { title: 'Entry', instructions: '', inputFields: [], outputFields: [], tools: [] }
          },
          {
            id: 'exit',
            type: 'Exit',
            position: { x: 0, y: 0 },
            data: { title: 'Exit', instructions: '', inputFields: [], outputFields: [], tools: [] }
          }
        ],
        edges: [{ id: 'e1', source: 'entry', target: 'exit' }]
      };
      
      const result = validateGraph(graph);
      expect(result.warnings.length).toBeGreaterThan(0);
    });

    it('should detect cyclic edges', () => {
      const cyclicGraph = {
        metadata: {
          user_intent: 'Test',
          role_count: 1,
          node_count: 2,
          created_at: new Date().toISOString(),
          design_version: '1.0.0'
        },
        nodes: [
          {
            id: 'node1',
            type: 'Agent',
            position: { x: 0, y: 0 },
            data: { title: 'Node1', instructions: '', inputFields: [], outputFields: [], tools: [] }
          },
          {
            id: 'node2',
            type: 'Agent',
            position: { x: 0, y: 0 },
            data: { title: 'Node2', instructions: '', inputFields: [], outputFields: [], tools: [] }
          }
        ],
        edges: [
          { id: 'e1', source: 'node1', target: 'node2' },
          { id: 'e2', source: 'node2', target: 'node1' }
        ]
      };
      
      const result = validateGraph(cyclicGraph);
      expect(result.isValid).toBe(false);
      expect(result.errors.length).toBe(1);
    });

    it('should detect incomplete metadata', () => {
      const incompleteGraph = {
        metadata: { user_intent: 'Test', role_count: -1, node_count: 0, created_at: 'invalid', design_version: '1.0.0' },
        nodes: [],
        edges: []
      } as any;
      
      const result = validateGraph(incompleteGraph);
      // Graph with empty nodes should fail validation
      expect(result.isValid).toBe(false);
    });

    it('should handle empty graph', () => {
      const emptyGraph = {
        metadata: { user_intent: 'Test', role_count: 0, node_count: 0, created_at: new Date().toISOString(), design_version: '1.0.0' },
        nodes: [],
        edges: []
      };
      
      const result = validateGraph(emptyGraph);
      expect(result.isValid).toBe(false);
    });

    it('should truncate long error lists', () => {
      const invalidGraph = {
        metadata: { user_intent: 'Test', role_count: 1, node_count: 5, created_at: new Date().toISOString(), design_version: '1.0.0' },
        nodes: Array(5).fill(null).map((_, i) => ({
          id: `node${i}`,
          type: 'Agent',
          position: { x: 0, y: 0 },
          data: { title: '', instructions: '', inputFields: [], outputFields: [], tools: [] }
        })),
        edges: [
          { id: 'e1', source: 'node0', target: 'node1' },
          { id: 'e2', source: 'node1', target: 'node2' },
          { id: 'e3', source: 'node2', target: 'node3' },
          { id: 'e4', source: 'node3', target: 'node4' }
        ]
      };
      
      const result = validateGraph(invalidGraph);
      expect(result.errors.length).toBeLessThanOrEqual(5);
    });

    it('should truncate long warning lists', () => {
      const graph = {
        metadata: { user_intent: 'Test', role_count: 0, node_count: 3, created_at: new Date().toISOString(), design_version: '1.0.0' },
        nodes: Array(3).fill(null).map((_, i) => ({
          id: `node${i}`,
          type: 'Agent',
          position: { x: 0, y: 0 },
          data: { title: `Node${i}`, instructions: '', inputFields: [], outputFields: [], tools: [] }
        })),
        edges: [{ id: 'e1', source: 'node0', target: 'node1' }]
      };
      
      const result = validateGraph(graph);
      expect(result.warnings.length).toBeLessThanOrEqual(3);
    });
  });
});

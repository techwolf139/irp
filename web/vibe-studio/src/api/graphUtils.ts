import { GraphData, Node, NodeType } from './graph'
import { v4 as uuidv4 } from 'uuid'

export function createEmptyGraph(userIntent: string): GraphData {
  return {
    metadata: {
      user_intent: userIntent,
      role_count: 0,
      node_count: 0,
      created_at: new Date().toISOString(),
      design_version: '1.0.0'
    },
    nodes: createEntryAndExitNodes(),
    edges: []
  }
}

export function createEntryAndExitNodes(): Node[] {
  return [
    {
      id: 'entry',
      type: 'Entry',
      position: { x: 100, y: 300 },
      data: {
        role: 'entry',
        title: '入口节点',
        instructions: '工作流入口',
        inputFields: [],
        outputFields: [],
        tools: []
      }
    },
    {
      id: 'exit',
      type: 'Exit',
      position: { x: 600, y: 300 },
      data: {
        role: 'exit',
        title: '出口节点',
        instructions: '工作流出口',
        inputFields: [],
        outputFields: [],
        tools: []
      }
    }
  ]
}

export function createAgentNode(
  id: string,
  role: string,
  title: string
): Node {
  return {
    id,
    type: 'Agent',
    position: { x: 300, y: 300 },
    data: {
      role,
      title,
      instructions: '',
      inputFields: [],
      outputFields: [],
      tools: [],
      status: 'pending'
    }
  }
}

export function addNode(data: GraphData, newNode: Node): GraphData {
  const existingNodes = data.nodes.filter(n => n.id !== newNode.id)
  return {
    ...data,
    nodes: [...existingNodes, newNode],
    metadata: {
      ...data.metadata,
      node_count: existingNodes.length + 1
    }
  }
}

export function addEdge(data: GraphData, newEdge: Edge): GraphData {
  return {
    ...data,
    edges: [...data.edges, newEdge]
  }
}

export function validateGraph(data: GraphData): ValidationResult {
  const errors: string[] = []
  const warnings: string[] = []
  
  // Check if all nodes have required fields
  for (const node of data.nodes) {
    if (!node.data.title) {
      errors.push(`Node "${node.id}" missing title`)
    }
    if (!node.data.instructions) {
      warnings.push(`Node "${node.id}" missing instructions`)
    }
  }
  
  // Check for circular dependencies
  const hasCircular = detectCyclicEdges(data.edges)
  if (hasCircular) {
    errors.push('Circular dependency detected')
  }
  
  return {
    isValid: errors.length === 0,
    errors: errors.slice(0, 5),
    warnings: warnings.slice(0, 3)
  }
}

function detectCyclicEdges(edges: Edge[]): boolean {
  // Simple cycle detection - in production use DFS
  const edgeSet = new Set(edges.map(e => `${e.source}-${e.target}`))
  return Array.from(edgeSet).some(edge => {
    const [from, to] = edge.split('-')
    return edgeSet.has(`${to}-${from}`)
  })
}

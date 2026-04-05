// Graph 类型定义
export interface GraphData {
  nodes: Node[]
  edges: Edge[]
  metadata: GraphMetadata
}

export interface Node {
  id: string
  type: NodeType
  position: { x: number; y: number }
  data: NodeData
  selected?: boolean
}

export interface NodeData {
  role: string
  title: string
  instructions: string
  inputFields: string[]
  outputFields: string[]
  tools: string[]
  status?: 'pending' | 'running' | 'completed' | 'failed'
}

export interface Edge {
  id: string
  source: string
  target: string
  animated?: boolean
  style?: { stroke?: string, strokeWidth?: number }
}

export interface GraphMetadata {
  user_intent: string
  role_count: number
  node_count: number
  created_at: string
  design_version: string
}

export type NodeType = 
  | 'Entry'
  | 'Exit'
  | 'Agent'
  | 'Graph'
  | 'Loop'
  | 'Switch'
  | 'Interaction'

export interface GenerateRequest {
  user_intent: string
  role_count?: number
  topology_type?: 'linear' | 'parallel' | 'hierarchical'
}

export interface ValidationResult {
  isValid: boolean
  errors: string[]
  warnings: string[]
}

/**
 * VibeGraph API for Web Application
 * 
 * Provides interfaces and utilities for interacting with the VibeGraph backend
 */

import axios from 'axios'

const API_BASE = '/api/v1'

export interface GenerateRequest {
  user_intent: string
  role_count?: number
  topology_type?: 'linear' | 'parallel' | 'hierarchical'
}

export interface RoleAssignment {
  name: string
  role: string
  skills: string[]
}

export interface GraphTopology {
  nodes: { id: string; type: string }[]
  edges: { source: string; target: string }[]
  metadata: {
    type: string
    node_count: number
    edge_count: number
  }
}

export interface SemanticCompletion {
  nodes: {
    id: string
    type: string
    instructions: string
    input_fields: string[]
    output_fields: string[]
    tools: string[]
  }[]
  edges: { source: string; target: string }[]
}

export interface VibeGraphResponse {
  config: SemanticCompletion
  metadata: GraphTopology['metadata']
}

export interface ValidationResult {
  isValid: boolean
  errors: string[]
  warnings: string[]
}

class VibeGraphApi {
  private baseURL: string

  constructor(baseURL: string) {
    this.baseURL = baseURL
  }

  /**
   * Generate VibeGraph from natural language description
   */
  async generate(config: GenerateRequest): Promise<VibeGraphResponse> {
    const response = await axios.post<GenerateRequest, { data: VibeGraphResponse }>(
      `${this.baseURL}/vibe/build`,
      config
    )
    return response.data
  }

  /**
   * Preview graph design before execution
   */
  async preview(designId: string): Promise<GraphTopology> {
    const response = await axios.get<GraphTopology>(
      `${this.baseURL}/vibe/preview?design_id=${designId}`
    )
    return response.data
  }

  /**
   * Execute a generated graph
   */
  async execute(graphId: string, runParams: Record<string, any>): Promise<any> {
    const response = await axios.post(`${this.baseURL}/vibe/execute`, {
      graph_id: graphId,
      run_params: runParams
    })
    return response.data
  }

  /**
   * Get user feedback on generated design
   */
  async feedback(feedbackRequest: Record<string, any>): Promise<{ success: boolean }> {
    const response = await axios.post(`${this.baseURL}/vibe/feedback`, feedbackRequest)
    return response.data
  }

  /**
   * Get history of user's generated graphs
   */
  async getHistory(): Promise<VibeGraphResponse[]> {
    const response = await axios.get<VibeGraphResponse[]>(`${this.baseURL}/vibe/history`)
    return response.data
  }

  /**
   * Validate a graph design
   */
  async validate(design: SemanticCompletion): Promise<ValidationResult> {
    const response = await axios.post<ValidateData, ValidateResponse>(
      `${this.baseURL}/vibe/validate`,
      { design }
    )
    return response.data
  }
}

export default new VibeGraphApi(API_BASE)
export const vibeGraphApi = new VibeGraphApi(API_BASE)

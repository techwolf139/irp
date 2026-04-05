import React from 'react'

export interface VibeGraphState {
  user_intent: string
  node_count: number
  role_count: number
  generated_at: string
  is_generating: boolean
  nodes: any[]
  edges: any[]
}

export interface VibeGraphState {
  user_intent: string
  node_count: number
  role_count: number
  generated_at: string
  is_generating: boolean
  nodes: any[]
  edges: any[]
}

export interface GenerateRequest {
  user_intent: string
  role_count?: number
  topology_type?: 'linear' | 'parallel' | 'hierarchical'
}

export interface GenerateResponse {
  config: any
  metadata: {
    nodes_count: number
    edges_count: number
    roles: any[]
  }
}

export const useVibeGraph = () => {
  const [state, setState] = React.useState<VibeGraphState>({
    user_intent: '',
    node_count: 0,
    role_count: 0,
    generated_at: '',
    is_generating: false,
    nodes: [],
    edges: []
  })

  async function generateGraph(config: GenerateRequest) {
    try {
      setState(prev => ({ ...prev, is_generating: true }))
      
      const response = await fetch('/api/v1/vibe/build', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      })
      
      const data: GenerateResponse = await response.json()
      
      setState({
        user_intent: config.user_intent,
        node_count: data.metadata.nodes_count,
        role_count: data.metadata.roles?.length || 0,
        generated_at: new Date().toISOString(),
        is_generating: false,
        nodes: data.config?.nodes || [],
        edges: data.config?.edges || []
      })
    } catch (error) {
      console.error('VibeGraph generation failed:', error)
      setState(prev => ({ ...prev, is_generating: false }))
      throw error
    }
  }

  return {
    state,
    generateGraph,
    reset: () => setState({
      user_intent: '',
      node_count: 0,
      role_count: 0,
      generated_at: '',
      is_generating: false,
      nodes: [],
      edges: []
    })
  }
}

export const VibeGraphService = {
  async generate(config: GenerateRequest): Promise<GenerateResponse> {
    const response = await fetch('/api/v1/vibe/build', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config)
    })
    return await response.json()
  }
}

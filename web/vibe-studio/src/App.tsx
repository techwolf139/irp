import React from 'react'
import { VibeInput, DesignPreview } from './VibeInput'
import { GraphEditor } from './GraphEditor'
import { NodePanel } from './NodePanel'
import { useVibeGraph } from '../hooks/useVibeGraph'

export const App: React.FC = () => {
  const { state, generateGraph } = useVibeGraph()

  const handleGenerate = async (intent: string) => {
    try {
      await generateGraph({
        user_intent: intent,
        topology_type: 'linear'
      })
    } catch (error) {
      console.error('Generation failed:', error)
    }
  }

  return (
    <div className="app">
      <div className="header">
        <h1>IRP VibeGraph Studio</h1>
        <p>基于 MASFactory 的可视化工作流编排系统</p>
      </div>

      <div className="main-content">
        <div className="left-panel">
          <VibeInput 
            onGenerate={handleGenerate}
            isGenerating={state.is_generating}
          />
          <NodePanel onSelectNodeType={(type) => console.log('Selected:', type)} />
          <DesignPreview
            user_intent={state.user_intent}
            node_count={state.node_count}
            role_count={state.role_count}
            generated_at={state.generated_at}
          />
        </div>

        <div className="right-panel">
          <GraphEditor
            nodes={state.nodes}
            edges={state.edges}
          />
        </div>
      </div>

      {state.is_generating && (
        <div className="generating-overlay">
          <div className="generating-spinner">
            <span className="loader"></span>
            <p>正在生成 VibeGraph，请稍候...</p>
          </div>
        </div>
      )}
    </div>
  )
}

export default App

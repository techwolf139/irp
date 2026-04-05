import React, { useState } from 'react'

interface NodeItem {
  label: string
  type: string
  icon?: any
}

interface Props {
  onSelectNodeType: (type: string) => void
}

export const NodePanel: React.FC<Props> = ({ onSelectNodeType }) => {
  const [selectedNode, setSelectedNode] = useState<string | null>(null)

  const nodeTypes: NodeItem[] = [
    { label: 'Agent', type: 'Agent', icon: '🤖' },
    { label: 'Graph', type: 'Graph', icon: '📊' },
    { label: 'Loop', type: 'Loop', icon: '🔄' },
    { label: 'Switch', type: 'Switch', icon: '⚡' },
    { label: 'Entry', type: 'Entry', icon: '⏫' },
    { label: 'Exit', type: 'Exit', icon: '⏬' },
    { label: 'Interaction', type: 'Interaction', icon: '👤' }
  ]

  return (
    <div className="node-panel">
      <div className="panel-header">
        <h3>节点组件</h3>
        <p>选择要添加到图中的节点类型</p>
      </div>

      <div className="node-types">
        {nodeTypes.map(node => (
          <div 
            key={node.type}
            className={`node-type-item ${selectedNode === node.type ? 'selected' : ''}`}
            onClick={() => {
              setSelectedNode(node.type)
              onSelectNodeType(node.type)
            }}
          >
            <span className="node-icon">{node.icon}</span>
            <span className="node-label">{node.label}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

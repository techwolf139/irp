import React, { useRef, useCallback } from 'react'
import ReactFlow, { 
  MiniMap, 
  Controls, 
  Background, 
  NodeChange, 
  Node, 
  Edge 
} from 'reactflow'
import 'reactflow/dist/style.css'

import VibeGraphState from '../hooks/useVibeGraph'

export interface GraphEditorProps {
  nodes: Node[]
  edges: Edge[]
  onNodeAdd?: (type: string, position: {x: number, y: number}) => void
}

const customNodeStyles = {
  entry: { 
    background: '#d4edda',
    border: '1px solid #28a745',
    borderRadius: '50%',
    padding: '20px',
    minWidth: '80px'
  },
  exit: {
    background: '#f8d7da',
    border: '1px solid #dc3545',
    borderRadius: '50%',
    padding: '20px',
    minWidth: '80px'
  },
  agent: {
    background: '#e7f3ff',
    border: '1px solid #007bff',
    borderRadius: '4px',
    padding: '10px'
  },
  graph: {
    background: '#fff3cd',
    border: '1px solid #ffc107',
    borderRadius: '4px'
  },
  loop: {
    background: '#e2d9f3',
    border: '1px solid #6f42c1',
    borderRadius: '4px'
  }
}

export const GraphEditor: React.FC<GraphEditorProps> = ({ nodes, edges }) => {
  const reactFlowWrapper = useRef<HTMLDivElement>(null)
  const [reactFlowInstance, setReactFlowInstance] = useState<any>(null)

  const onNodeInit = useCallback((reactFlowInstance: any) => {
    setReactFlowInstance(reactFlowInstance)
    // 自动布局
    const layout = reactFlowInstance.fitView()
  }, [])

  const handleNodeAdd = useCallback((type: string, position: {x: number, y: number}) => {
    const newNode: Node = {
      id: `node_${Date.now()}`,
      type,
      position,
      data: {
        label: type === 'agent' ? 'Agent 节点' : type
      }
    }
    reactFlowInstance?.addNodes(newNode)
  }, [reactFlowInstance])

  if (!nodes.length) {
    return (
      <div className="graph-empty" ref={reactFlowWrapper}>
        <div className="empty-state">
          <span className="empty-icon">📊</span>
          <p>请先生成 VibeGraph 或使用节点面板添加节点</p>
        </div>
      </div>
    )
  }

  return (
    <div className="graph-editor" ref={reactFlowWrapper}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onInit={onNodeInit}
        fitView={true}
        fitViewOptions={{ padding: 0.1 }}
        minZoom={0.1}
        maxZoom={2}
      >
        <Controls />
        <MiniMap 
          nodeStrokeColor={color => `#007bff`}
          nodeColor="#007bff"
          maskColor="rgba(0,0,0,0.1)"
          style={{ background: '#fff' }}
        />
        <Background color="#aaa" gap={16} />
      </ReactFlow>
    </div>
  )
}

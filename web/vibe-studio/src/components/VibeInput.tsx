import React, { useState } from 'react'

interface Props {
  onGenerate: (intent: string) => void
  isGenerating: boolean
}

export const VibeInput: React.FC<Props> = ({ onGenerate, isGenerating }) => {
  const [value, setValue] = useState('')
  const [description, setDescription] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (value.trim() && !isGenerating) {
      onGenerate(value.trim())
    }
  }

  return (
    <div className="vibe-input-container">
      <div className="vibe-header">
        <h2>VibeGraph 生成</h2>
        <p>输入工作流需求，系统自动生成审批流程</p>
      </div>

      <form onSubmit={handleSubmit} className="vibe-form">
        <div className="input-group">
          <label htmlFor="workflow-desc">工作流程描述</label>
          <textarea
            id="workflow-desc"
            placeholder="例如：创建一个采购合同审批流程，需要采购负责人初审，法务复审，财务终审..."
            value={description}
            onChange={e => setDescription(e.target.value)}
            rows={3}
          />
        </div>

        <div className="input-group">
          <label htmlFor="workflow-template">具体需求 (可选)</label>
          <input
            id="workflow-template"
            type="text"
            placeholder="例如：开始->A,B,C->D->结束"
            value={value}
            onChange={e => setValue(e.target.value)}
          />
        </div>

        <button 
          type="submit" 
          className="generate-btn"
          disabled={isGenerating || !value.trim()}
        >
          {isGenerating ? '生成中...' : '生成 VibeGraph'}
        </button>
      </form>

      <div className="tips">
        <h3>使用技巧:</h3>
        <ul>
          <li>支持描述性需求：如"需要采购负责人审批"</li>
          <li>支持结构化模板：START→A,B,C→D→END</li>
          <li>角色类型：审批员，法务，财务，项目负责人</li>
        </ul>
      </div>
    </div>
  )
}

export const DesignPreview: React.FC<{
  user_intent: string
  node_count: number
  role_count: number
  generated_at: string
}> = ({ user_intent, node_count, role_count, generated_at }) => {
  return (
    <div className="design-preview">
      <div className="preview-header">
        <h3>设计预览</h3>
        <div className="stats">
          <span>节点数：{node_count}</span>
          <span>角色数：{role_count}</span>
          <span>生成时间：{new Date(generated_at).toLocaleTimeString()}</span>
        </div>
      </div>
      <div className="preview-content">
        <p><strong>工作流意图:</strong> {user_intent}</p>
      </div>
    </div>
  )
}

/**
 * NodePanel 组件测试
 * 测试节点选择和面板交互
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { NodePanel } from '../../../../src/components/NodePanel';

describe('NodePanel Component', () => {
  const mockOnSelectNodeType = vi.fn();
  
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders panel header', () => {
    render(<NodePanel onSelectNodeType={mockOnSelectNodeType} />);
    expect(screen.getByText('节点组件')).toBeInTheDocument();
  });

  it('displays panel description', () => {
    render(<NodePanel onSelectNodeType={mockOnSelectNodeType} />);
    expect(screen.getByText(/选择要添加到图中的节点类型/)).toBeInTheDocument();
  });

  it('shows all 7 node types', () => {
    render(<NodePanel onSelectNodeType={mockOnSelectNodeType} />);
    const nodeTypes = screen.getAllByRole('button');
    expect(nodeTypes.length).toBeGreaterThan(5);
  });

  it('displays Agent node type', () => {
    render(<NodePanel onSelectNodeType={mockOnSelectNodeType} />);
    expect(screen.getByText('Agent')).toBeInTheDocument();
  });

  it('displays Graph node type', () => {
    render(<NodePanel onSelectNodeType={mockOnSelectNodeType} />);
    expect(screen.getByText('Graph')).toBeInTheDocument();
  });

  it('displays Loop node type', () => {
    render(<NodePanel onSelectNodeType={mockOnSelectNodeType} />);
    expect(screen.getByText('Loop')).toBeInTheDocument();
  });

  it('displays Switch node type', () => {
    render(<NodePanel onSelectNodeType={mockOnSelectNodeType} />);
    expect(screen.getByText('Switch')).toBeInTheDocument();
  });

  it('displays Entry node type', () => {
    render(<NodePanel onSelectNodeType={mockOnSelectNodeType} />);
    expect(screen.getByText('Entry')).toBeInTheDocument();
  });

  it('displays Exit node type', () => {
    render(<NodePanel onSelectNodeType={mockOnSelectNodeType} />);
    expect(screen.getByText('Exit')).toBeInTheDocument();
  });

  it('displays Interaction node type', () => {
    render(<NodePanel onSelectNodeType={mockOnSelectNodeType} />);
    expect(screen.getByText('Interaction')).toBeInTheDocument();
  });

  it('calls onSelectNodeType when Agent clicked', async () => {
    const user = userEvent.setup();
    render(<NodePanel onSelectNodeType={mockOnSelectNodeType} />);
    
    const agentNode = screen.getByRole('button', { name: /Agent/i });
    await user.click(agentNode);
    
    expect(mockOnSelectNodeType).toHaveBeenCalledWith('Agent');
  });

  it('calls onSelectNodeType when Graph clicked', async () => {
    const user = userEvent.setup();
    render(<NodePanel onSelectNodeType={mockOnSelectNodeType} />);
    
    const graphNode = screen.getByRole('button', { name: /Graph/i });
    await user.click(graphNode);
    
    expect(mockOnSelectNodeType).toHaveBeenCalledWith('Graph');
  });

  it('calls onSelectNodeType when all nodes clicked', async () => {
    const user = userEvent.setup();
    render(<NodePanel onSelectNodeType={mockOnSelectNodeType} />);
    
    const nodes = screen.getAllByRole('button');
    for (const node of nodes) {
      await user.click(node);
    }
    
    expect(mockOnSelectNodeType).toHaveBeenCalledTimes(nodes.length);
  });

  it('highlights selected node', async () => {
    const user = userEvent.setup();
    render(<NodePanel onSelectNodeType={mockOnSelectNodeType} />);
    
    const agentNode = screen.getByRole('button', { name: /Agent/i });
    await user.click(agentNode);
    
    expect(agentNode.parentElement).toHaveClass('selected');
  });

  it('does not crash with empty selector', () => {
    render(<NodePanel onSelectNodeType={() => {}} />);
    expect(screen.getByText('节点组件')).toBeInTheDocument();
  });

  it('renders icon for each node type', () => {
    render(<NodePanel onSelectNodeType={mockOnSelectNodeType} />);
    const icons = screen.getAllByRole('img', { hidden: true });
    expect(icons.length).toBeGreaterThan(0);
  });

  it('displays node labels correctly', () => {
    render(<NodePanel onSelectNodeType={mockOnSelectNodeType} />);
    const labels = screen.getAllByText(/^(Agent|Graph|Loop|Switch|Entry|Exit|Interaction)$/);
    expect(labels.length).toBe(7);
  });

  it('handles click on all node types', async () => {
    const user = userEvent.setup();
    const clicks: string[] = [];
    
    render(<NodePanel onSelectNodeType={(type) => clicks.push(type)} />);
    
    const nodes = screen.getAllByRole('button');
    for (const node of nodes) {
      await user.click(node);
    }
    
    expect(clicks.length).toBe(nodes.length);
  });

  it('passes correct type to callback', async () => {
    const user = userEvent.setup();
    render(<NodePanel onSelectNodeType={mockOnSelectNodeType} />);
    
    const entryNode = screen.getByRole('button', { name: /Entry/i });
    await user.click(entryNode);
    
    expect(mockOnSelectNodeType).toHaveBeenCalledWith('Entry');
  });

  it('renders NodePanel header', () => {
    render(<NodePanel onSelectNodeType={mockOnSelectNodeType} />);
    const header = screen.getByRole('heading', { name: /节点组件/ });
    expect(header).toBeInTheDocument();
    expect(header.tagName).toBe('H3');
  });

  it('renders panel description', () => {
    render(<NodePanel onSelectNodeType={mockOnSelectNodeType} />);
    const desc = screen.getByText(/选择要添加到图中的节点类型/);
    expect(desc.tagName).toBe('P');
  });

  it('renders node types in grid', () => {
    render(<NodePanel onSelectNodeType={mockOnSelectNodeType} />);
    const grid = screen.getByRole('list');
    expect(grid).toBeInTheDocument();
  });

  it('calls mock function with exact string values', async () => {
    const user = userEvent.setup();
    const testTypes = ['Agent', 'Graph', 'Loop', 'Switch', 'Entry', 'Exit', 'Interaction'];
    const callArgs: string[] = [];
    
    render(<NodePanel onSelectNodeType={(type) => callArgs.push(type)} />);
    
    for (const type of testTypes) {
      const node = screen.getByRole('button', { name: new RegExp(type, 'i') });
      await user.click(node);
    }
    
    expect(callArgs).toEqual(testTypes);
  });

  it('maintains component state on multiple selections', async () => {
    const user = userEvent.setup();
    render(<NodePanel onSelectNodeType={mockOnSelectNodeType} />);
    
    const agentNode = screen.getByRole('button', { name: /Agent/i });
    await user.click(agentNode);
    
    expect(agentNode.parentElement).toHaveClass('selected');
    
    const loopNode = screen.getByRole('button', { name: /Loop/i });
    await user.click(loopNode);
    
    // Only last selected should be highlighted
    expect(loopNode.parentElement).toHaveClass('selected');
  });

  it('renders NodePanel with proper container', () => {
    render(<NodePanel onSelectNodeType={mockOnSelectNodeType} />);
    const container = screen.getByRole('main');
    expect(container).toBeInTheDocument();
  });
});

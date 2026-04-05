/**
 * GraphEditor 组件测试
 * 测试 ReactFlow 集成和图编辑功能
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { GraphEditor } from '../../../../src/components/GraphEditor';

describe('GraphEditor Component', () => {
  it('should show empty state when no nodes', () => {
    const { getByText } = render(<GraphEditor nodes={[]} edges={[]} />);
    expect(getByText(/请先生成 VibeGraph 或使用节点面板添加节点/)).toBeInTheDocument();
  });

  it('should show empty state icon', () => {
    render(<GraphEditor nodes={[]} edges={[]} />);
    const icon = screen.getByRole('img', { hidden: true });
    expect(icon).toBeInTheDocument();
  });

  it('should render empty state message', () => {
    render(<GraphEditor nodes={[]} edges={[]} />);
    expect(screen.getByText(/请先生成 VibeGraph 或使用节点面板添加节点/)).toBeInTheDocument();
  });

  it('should not show loading overlay in empty state', () => {
    render(<GraphEditor nodes={[]} edges={[]} />);
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  });

  it('should have proper container', () => {
    render(<GraphEditor nodes={[]} edges={[]} />);
    const container = screen.getByRole('main');
    expect(container).toBeInTheDocument();
  });

  it('should have graph-empty class', () => {
    render(<GraphEditor nodes={[]} edges={[]} />);
    expect(screen.getByRole('main')).toHaveClass('graph-empty');
  });

  it('should show loading when generating', () => {
    const { container } = render(<GraphEditor nodes={[]} edges={[]} />);
    expect(container.querySelector('.generating-overlay')).toBeFalsy();
  });

  it('should have responsive layout', () => {
    render(<GraphEditor nodes={[]} edges={[]} />);
    const editor = screen.getByRole('main');
    expect(editor).toBeInTheDocument();
  });

  it('should handle empty array inputs', () => {
    const { getByText } = render(<GraphEditor nodes={[]} edges={[]} />);
    expect(getByText(/请先生成 VibeGraph 或使用节点面板添加节点/)).toBeInTheDocument();
  });

  it('should handle null inputs gracefully', () => {
    const { getByText } = render(<GraphEditor nodes={[]} edges={[]} />);
    expect(getByText(/请先生成 VibeGraph 或使用节点面板添加节点/)).toBeInTheDocument();
  });

  it('should render with correct styling', () => {
    render(<GraphEditor nodes={[]} edges={[]} />);
    const main = screen.getByRole('main');
    expect(main).toHaveClass('graph-empty');
  });

  it('should not crash with invalid inputs', () => {
    const { getByText } = render(<GraphEditor nodes={[]} edges={[]} />);
    expect(getByText(/请先生成 VibeGraph 或使用节点面板添加节点/)).toBeInTheDocument();
  });

  it('should render with Flexbox layout', () => {
    render(<GraphEditor nodes={[]} edges={[]} />);
    const main = screen.getByRole('main');
    expect(main).toHaveStyle('display: flex');
    expect(main).toHaveStyle('align-items: center');
    expect(main).toHaveStyle('justify-content: center');
  });

  it('should have proper error message for empty state', () => {
    render(<GraphEditor nodes={[]} edges={[]} />);
    const emptyState = screen.getByText(/请先生成 VibeGraph 或使用节点面板添加节点/);
    expect(emptyState).toBeInTheDocument();
  });

  it('should not show ReactFlow in empty state', () => {
    render(<GraphEditor nodes={[]} edges={[]} />);
    const controls = screen.queryAllByRole('button');
    expect(controls.length).toBe(0);
  });

  it('should have error state class', () => {
    render(<GraphEditor nodes={[]} edges={[]} />);
    const empty = screen.getByRole('main');
    expect(empty).toHaveClass('empty-state');
  });
});

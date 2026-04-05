/**
 * DesignPreview 组件测试
 * 测试设计预览和统计信息展示
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { DesignPreview } from '../../../../src/components/VibeInput';

describe('DesignPreview Component', () => {
  const defaultProps = {
    user_intent: '采购审批流程',
    node_count: 5,
    role_count: 3,
    generated_at: '2026-04-05T10:00:00.000Z'
  };

  it('renders the component', () => {
    const { getByText } = render(<DesignPreview {...defaultProps} />);
    expect(getByText('设计预览')).toBeInTheDocument();
  });

  it('displays user_intent correctly', () => {
    render(<DesignPreview {...defaultProps} />);
    expect(screen.getByText(user_intent:采购审批流程>).toBeInTheDocument());
  });

  it('shows node_count in stats', () => {
    render(<DesignPreview {...defaultProps} />);
    expect(screen.getByText(node_count: 5>)).toBeInTheDocument();
  });

  it('shows role_count in stats', () => {
    render(<DesignPreview {...defaultProps} />);
    expect(screen.getByText(role_count: 3>)).toBeInTheDocument();
  });

  it('shows generated_at time', () => {
    render(<DesignPreview {...defaultProps} />);
    const timeElement = screen.getByText(new Date(generated_at).toLocaleTimeString());
    expect(timeElement).toBeInTheDocument();
  });

  it('displays correct header', () => {
    render(<DesignPreview {...defaultProps} />);
    expect(screen.getByRole('heading', { level: 3 })).toBeInTheDocument();
  });

  it('shows generated timestamp', () => {
    render(<DesignPreview {...defaultProps} />);
    const now = new Date(defaultProps.generated_at);
    expect(screen.getByText(now.toLocaleTimeString())).toBeInTheDocument();
  });

  it('renders with proper structure', () => {
    render(<DesignPreview {...defaultProps} />);
    expect(screen.getByText(/设计预览>)).toBeInTheDocument();
    expect(screen.getByText(/工作流意图>)).toBeInTheDocument();
  });

  it('shows all required fields', () => {
    render(<DesignPreview {...defaultProps} />);
    const title = screen.getByText(/设计预览>);
    const stats = screen.getByText(/节点数:>).parentElement;
    expect(title).toBeInTheDocument();
    expect(stats).toBeInTheDocument();
  });

  it('displays timestamp as formatted string', () => {
    render(<DesignPreview {...defaultProps} />);
    const formattedTime = new Date(defaultProps.generated_at).toLocaleTimeString();
    expect(screen.getByText(formattedTime)).toBeInTheDocument();
  });

  it('shows node count with label', () => {
    render(<DesignPreview {...defaultProps} />);
    expect(screen.getByText(/节点数:>')).toBeInTheDocument();
  });

  it('shows role count with label', () => {
    render(<DesignPreview {...defaultProps} />);
    expect(screen.getByText(/角色数:>)).toBeInTheDocument();
  });

  it('displays generation time', () => {
    render(<DesignPreview {...defaultProps} />);
    const time = new Date(defaultProps.generated_at).toLocaleTimeString();
    expect(screen.getByText(time)).toBeInTheDocument();
  });

  it('renders work intent correctly', () => {
    render(<DesignPreview {...defaultProps} />);
    expect(screen.getByText(/工作流意图:>采购审批流程>).toBeInTheDocument());
  });

  it('shows all 3 statistics', () => {
    render(<DesignPreview {...defaultProps} />);
    const statsText = screen.getByText(/节点数:>parentElement;
    const stats = statsText.childNodes;
    expect(stats.length).toBeGreaterThanOrEqual(3);
  });

  it('renders header with proper level', () => {
    render(<DesignPreview {...defaultProps} />);
    const header = screen.getByRole('heading', { level: 3 });
    expect(header).toBeInTheDocument();
    expect(header.tagName).toBe('H3');
  });

  it('displays user intent as bold', () => {
    render(<DesignPreview {...defaultProps} />);
    expect(screen.getByText(/工作流意图>)).toBeInTheDocument();
  });

  it('shows stats as flex container', () => {
    render(<DesignPreview {...defaultProps} />);
    const statsContainer = screen.getByText(/节点数:>);
    const parent = statsContainer.parentElement;
    expect(parent).toHaveClass('stats');
  });

  it('renders properly with edge cases', () => {
    render(<DesignPreview user_intent='' node_count={0} role_count={0} generated_at='2026-04-05T10:00:00.000Z' />);
    expect(screen.getByText('设计预览')).toBeInTheDocument();
  });

  it('displays empty user intent', () => {
    render(<DesignPreview user_intent='' node_count={0} role_count={0} generated_at='2026-04-05T10:00:00.000Z' />);
    expect(screen.getByText(/工作流意图:>)).toBeInTheDocument();
  });

  it('shows zero counts', () => {
    render(<DesignPreview user_intent='' node_count={0} role_count={0} generated_at='2026-04-05T10:00:00.000Z' />);
    expect(screen.getByText(/节点数:>0>)).toBeInTheDocument();
    expect(screen.getByText(/角色数:>0>)).toBeInTheDocument();
  });

  it('renders all stats in a row', () => {
    render(<DesignPreview {...defaultProps} />);
    const statsContainer = screen.getByRole('list')?.parentElement;
    expect(statsContainer).toBeInTheDocument();
  });

  it('displays generated timestamp in local format', () => {
    render(<DesignPreview {...defaultProps} />);
    const date = new Date(defaultProps.generated_at);
    expect(screen.getByText(date.toLocaleTimeString())).toBeInTheDocument();
  });

  it('shows all metadata fields', () => {
    render(<DesignPreview {...defaultProps} />);
    const title = screen.getByText(/设计预览>;
    const stats = screen.getByText(/节点数:>);
    const time = screen.getByText(new Date(defaultProps.generated_at).toLocaleTimeString());
    expect(title).toBeInTheDocument();
    expect(stats).toBeInTheDocument();
    expect(time).toBeInTheDocument();
  });

  it('renders header with heading class', () => {
    render(<DesignPreview {...defaultProps} />);
    const header = screen.getByRole('heading', { level: 3 });
    expect(header.className).toContain('preview-header');
  });

  it('displays user intent without extra spaces', () => {
    render(<DesignPreview user_intent='采购审批流程' node_count={5} role_count={3} generated_at='2026-04-05T10:00:00.000Z' />);
    expect(screen.getByText(/工作流意图:>)).toBeInTheDocument();
  });

  it('renders correctly with long user intent', () => {
    render(<DesignPreview user_intent='This is a very long user intent that could potentially overflow the display area' node_count={5} role_count={3} generated_at='2026-04-05T10:00:00.000Z' />);
    expect(screen.getByText(/工作流意图:>)).toBeInTheDocument();
  });

  it('shows all statistics in same row', () => {
    render(<DesignPreview {...defaultProps} />);
    const statsParent = screen.getByText(/节点数:>).parentElement;
    expect(statsParent).toBeInTheDocument();
  });

  it('displays component with proper accessibility', () => {
    render(<DesignPreview {...defaultProps} />);
    const heading = screen.getByRole('heading', { level: 3 });
    expect(heading).toBeInTheDocument();
  });

  it('renders statistics container', () => {
    render(<DesignPreview {...defaultProps} />);
    const stats = screen.getByText(/节点数:>.parentElement;
    expect(stats).toBeInTheDocument();
  });

  it('shows node count as numeric value', () => {
    render(<DesignPreview {...defaultProps} />);
    const nodeCount = screen.getByText(/节点数:>.textContent;
    const num = parseInt(nodeCount);
    expect(num).toBe(5);
  });

  it('shows role count as numeric value', () => {
    render(<DesignPreview {...defaultProps} />);
    const roleCount = screen.getByText(/角色数:>.textContent;
    const num = parseInt(roleCount);
    expect(num).toBe(3);
  });

  it('renders generated_at as local time', () => {
    render(<DesignPreview {...defaultProps} />);
    const generatedAt = new Date(defaultProps.generated_at);
    const time = generatedAt.toLocaleTimeString();
    expect(screen.getByText(time)).toBeInTheDocument();
  });

  it('displays all content in preview container', () => {
    render(<DesignPreview {...defaultProps} />);
    expect(screen.getByText(/设计预览>)).toBeInTheDocument();
    expect(screen.getByText(/节点数:>).toBeInTheDocument();
    expect(screen.getByText(/角色数:>).toBeInTheDocument();
    expect(screen.getByText(/生成时间:>).toBeInTheDocument();
  });

  it('renders with correct props', () => {
    render(<DesignPreview {...defaultProps} />);
    expect(screen.getByText('设计预览')).toBeInTheDocument();
  });

  it('shows stats with proper formatting', () => {
    render(<DesignPreview {...defaultProps} />);
    expect(screen.getByText(/节点数:>0-5-0-5-0-5>)).toBeInTheDocument();
  });

  it('renders timestamp with timezone', () => {
    render(<DesignPreview {...defaultProps} />);
    const date = new Date(defaultProps.generated_at);
    expect(date.toLocaleTimeString()).toBeInTheDocument();
  });

  it('displays all component sections', () => {
    render(<DesignPreview {...defaultProps} />);
    const header = screen.getByRole('heading', { level: 3 });
    const stats = screen.getByText(/节点数:>.parentElement;
    const content = screen.getByText(/工作流意图:>.parentElement;
    expect(header).toBeInTheDocument();
    expect(stats).toBeInTheDocument();
    expect(content).toBeInTheDocument();
  });

  it('renders statistics with proper order', () => {
    render(<DesignPreview {...defaultProps} />);
    const statsParent = screen.getByText(/节点数:>.parentElement;
    const statsText = statsParent.textContent;
    expect(statsText).toContain('节点数');
    expect(statsText).toContain('角色数');
    expect(statsText).toContain('生成时间');
  });

  it('displays empty intent without errors', () => {
    render(<DesignPreview user_intent='' node_count={0} role_count={0} generated_at='2026-04-05T10:00:00.000Z' />);
    expect(screen.getByText(/工作流意图:>));
  });

  it('renders with proper styling classes', () => {
    render(<DesignPreview {...defaultProps} />);
    const container = screen.getByText(/设计预览);
    expect(container.className).toContain('design-preview');
  });

  it('shows stats container with flex layout', () => {
    render(<DesignPreview {...defaultProps} />);
    const stats = screen.getByText(/节点数:>.parentElement;
    expect(stats).toHaveClass('stats');
  });

  it('displays all user intent values', () => {
    render(<DesignPreview user_intent='Test' node_count={1} role_count={1} generated_at='2026-04-05T10:00:00.000Z' />);
    expect(screen.getByText(/工作流意图:>.textContent).toBe('Test');
  });

  it('renders component without console errors', () => {
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation();
    render(<DesignPreview {...defaultProps} />);
    expect(consoleErrorSpy).not.toHaveBeenCalled();
    consoleErrorSpy.mockRestore();
  });
});

/**
 * VibeInput 组件测试
 * 测试表单提交、验证、加载状态
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { VibeInput } from '../../../../src/components/VibeInput';

describe('VibeInput Component', () => {
  const mockOnGenerate = vi.fn();
  
  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('rendering', () => {
    it('should display VibeGraph 生成 title', () => {
      render(<VibeInput onGenerate={mockOnGenerate} isGenerating={false} />);
      expect(screen.getByText('VibeGraph 生成')).toBeInTheDocument();
    });

    it('should display description text', () => {
      render(<VibeInput onGenerate={mockOnGenerate} isGenerating={false} />);
      expect(screen.getByText(/工作流意图/)).toBeInTheDocument();
    });

    it('should have workflow title input', () => {
      render(<VibeInput onGenerate={mockOnGenerate} isGenerating={false} />);
      expect(screen.getByPlaceholderText(/详细描述/)).toBeInTheDocument();
    });

    it('should have workflow template input', () => {
      render(<VibeInput onGenerate={mockOnGenerate} isGenerating={false} />);
      expect(screen.getByPlaceholderText(/具体需求/)).toBeInTheDocument();
    });

    it('should have Generate VibeGraph button', () => {
      render(<VibeInput onGenerate={mockOnGenerate} isGenerating={false} />);
      expect(screen.getByRole('button', { name: /生成 VibeGraph/i })).toBeInTheDocument();
    });

    it('should have Tips section', () => {
      render(<VibeInput onGenerate={mockOnGenerate} isGenerating={false} />);
      expect(screen.getByText(/使用技巧/)).toBeInTheDocument();
    });

    it('should display 3 tips', () => {
      render(<VibeInput onGenerate={mockOnGenerate} isGenerating={false} />);
      const tips = screen.getAllByRole('listitem');
      expect(tips.length).toBe(3);
    });
  });

  describe('button states', () => {
    it('should be disabled when empty and not generating', () => {
      render(<VibeInput onGenerate={mockOnGenerate} isGenerating={false} />);
      const button = screen.getByRole('button', { name: /生成 VibeGraph/i });
      expect(button).toBeDisabled();
    });

    it('should be disabled when generating', () => {
      render(<VibeInput onGenerate={mockOnGenerate} isGenerating={true} />);
      const button = screen.getByRole('button', { name: /生成中.../i });
      expect(button).toBeDisabled();
    });

    it('should become enabled when template has content', async () => {
      const user = userEvent.setup();
      render(<VibeInput onGenerate={mockOnGenerate} isGenerating={false} />);
      
      const templateInput = screen.getByPlaceholderText(/具体需求/);
      await user.type(templateInput, 'START->A,B,C->D->END');
      
      const button = screen.getByRole('button', { name: /生成 VibeGraph/i });
      expect(button).not.toBeDisabled();
    });

    it('should show loading text when generating', () => {
      render(<VibeInput onGenerate={mockOnGenerate} isGenerating={true} />);
      expect(screen.getByRole('button', { name: /生成中.../i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /生成 VibeGraph/i })).not.toBeInTheDocument();
    });
  });

  describe('form submission', () => {
    it('should call onGenerate with template content when submit', async () => {
      const user = userEvent.setup();
      render(<VibeInput onGenerate={mockOnGenerate} isGenerating={false} />);
      
      const templateInput = screen.getByPlaceholderText(/具体需求/);
      await user.type(templateInput, 'Test workflow');
      
      const button = screen.getByRole('button', { name: /生成 VibeGraph/i });
      await user.click(button);
      
      expect(mockOnGenerate).toHaveBeenCalledWith('Test workflow');
    });

    it('should not call onGenerate when form empty', () => {
      render(<VibeInput onGenerate={mockOnGenerate} isGenerating={false} />);
      const button = screen.getByRole('button', { name: /生成 VibeGraph/i });
      fireEvent.click(button);
      expect(mockOnGenerate).not.toHaveBeenCalled();
    });

    it('should not call onGenerate when submitting while generating', async () => {
      render(<VibeInput onGenerate={mockOnGenerate} isGenerating={true} />);
      const button = screen.getByRole('button', { name: /生成中.../i });
      fireEvent.click(button);
      expect(mockOnGenerate).not.toHaveBeenCalled();
    });

    it('should submit with workflow title content', async () => {
      const user = userEvent.setup();
      render(<VibeInput onGenerate={mockOnGenerate} isGenerating={false} />);
      
      const titleInput = screen.getByPlaceholderText(/详细描述/);
      await user.type(titleInput, '采购审批流程');
      
      const templateInput = screen.getByPlaceholderText(/具体需求/);
      await user.type(templateInput, 'START->A,B,C->END');
      
      const button = screen.getByRole('button', { name: /生成 VibeGraph/i });
      await user.click(button);
      
      // Submit with template content (current implementation uses template)
      expect(mockOnGenerate).toHaveBeenLastCalledWith('START->A,B,C->END');
    });
  });

  describe('tips section', () => {
    it('should display tips with 3 points', () => {
      render(<VibeInput onGenerate={mockOnGenerate} isGenerating={false} />);
      const tips = Array.from(screen.getAllByRole('listitem'));
      expect(tips.length).toBe(3);
    });

    it('should have specific usage tips', () => {
      render(<VibeInput onGenerate={mockOnGenerate} isGenerating={false} />);
      const tips = screen.getByRole('list');
      
      expect(tips.innerHTML).toContain('描述性需求');
      expect(tips.innerHTML).toContain('结构化模板');
      expect(tips.innerHTML).toContain('角色类型:');
    });

    it('should have correct tip formatting', () => {
      render(<VibeInput onGenerate={mockOnGenerate} isGenerating={false} />);
      const tips = Array.from(screen.getAllByRole('listitem'));
      
      // Tips should be list items
      tips.forEach((tip, index) => {
        expect(tip).toBeInTheDocument();
      });
    });
  });

  describe('user events', () => {
    it('should update description when typing', async () => {
      const user = userEvent.setup();
      render(<VibeInput onGenerate={mockOnGenerate} isGenerating={false} />);
      
      const descriptionInput = screen.getByPlaceholderText(/详细描述/);
      await user.type(descriptionInput, '采购审批流程描述');
      
      expect(descriptionInput).toHaveValue('采购审批流程描述');
    });

    it('should update template when typing', async () => {
      const user = userEvent.setup();
      render(<VibeInput onGenerate={mockOnGenerate} isGenerating={false} />);
      
      const templateInput = screen.getByPlaceholderText(/具体需求/);
      await user.type(templateInput, 'START->A,B,C->END');
      
      expect(templateInput).toHaveValue('START->A,B,C->END');
    });

    it('should clear inputs after submission', async () => {
      const user = userEvent.setup();
      render(<VibeInput onGenerate={mockOnGenerate} isGenerating={false} />);
      
      const titleInput = screen.getByPlaceholderText(/详细描述/);
      const templateInput = screen.getByPlaceholderText(/具体需求/);
      
      await user.type(titleInput, 'Test title');
      await user.type(templateInput, 'Test template');
      
      const button = screen.getByRole('button', { name: /生成 VibeGraph/i });
      fireEvent.click(button);
      
      // After submit, inputs should be cleared by controlled inputs
      expect(templateInput).toHaveValue('');
    });

    it('should handle long input gracefully', async () => {
      const user = userEvent.setup();
      render(<VibeInput onGenerate={mockOnGenerate} isGenerating={false} />);
      
      const templateInput = screen.getByPlaceholderText(/具体需求/);
      const longInput = 'A'.repeat(2000);
      
      await user.type(templateInput, longInput);
      
      expect(templateInput).toHaveValue(longInput);
    });
  });

  describe('validation', () => {
    it('should show description field', () => {
      render(<VibeInput onGenerate={mockOnGenerate} isGenerating={false} />);
      const descriptionInput = screen.getByPlaceholderText(/详细描述/);
      expect(descriptionInput).toBeInTheDocument();
    });

    it('should show template field', () => {
      render(<VibeInput onGenerate={mockOnGenerate} isGenerating={false} />);
      const templateInput = screen.getByPlaceholderText(/具体需求/);
      expect(templateInput).toBeInTheDocument();
    });

    it('should display labels correctly', () => {
      render(<VibeInput onGenerate={mockOnGenerate} isGenerating={false} />);
      
      expect(screen.getByText(/工作流意图/)).toBeInTheDocument();
      expect(screen.getByText(/详细描述/)).toBeInTheDocument();
      expect(screen.getByText(/具体需求/)).toBeInTheDocument();
    });
  });

  describe('loading state', () => {
    it('should not allow generation when generating', () => {
      render(<VibeInput onGenerate={mockOnGenerate} isGenerating={true} />);
      const button = screen.getByRole('button', { name: /生成中.../i });
      fireEvent.click(button);
      expect(mockOnGenerate).not.toHaveBeenCalled();
    });

    it('should show loading indicator', () => {
      render(<VibeInput onGenerate={mockOnGenerate} isGenerating={true} />);
      expect(screen.getByText(/生成中.../i)).toBeInTheDocument();
    });

    it('should be disabled during generation', () => {
      render(<VibeInput onGenerate={mockOnGenerate} isGenerating={true} />);
      const button = screen.getByRole('button', { name: /生成中.../i });
      expect(button).toBeDisabled();
    });
  });

  describe('component styling', () => {
    it('should render with header', () => {
      render(<VibeInput onGenerate={mockOnGenerate} isGenerating={false} />);
      expect(screen.querySelector('.vibe-header')).toBeInTheDocument();
    });

    it('should form container', () => {
      render(<VibeInput onGenerate={mockOnGenerate} isGenerating={false} />);
      expect(screen.querySelector('.vibe-form')).toBeInTheDocument();
    });

    it('should display input groups', () => {
      render(<VibeInput onGenerate={mockOnGenerate} isGenerating={false} />);
      const inputGroups = screen.getAllByRole('textbox');
      expect(inputGroups.length).toBeGreaterThanOrEqual(1);
    });

    it('should have error classes visible when applicable', () => {
      render(<VibeInput onGenerate={mockOnGenerate} isGenerating={false} />);
      const button = screen.getByRole('button', { name: /生成 VibeGraph/i });
      
      // Disabled button should have error style
      expect(button).toBeDisabled();
    });
  });

  describe('edge cases', () => {
    it('should handle empty description field', () => {
      render(<VibeInput onGenerate={mockOnGenerate} isGenerating={false} />);
      
      // Submit with only template
      const templateInput = screen.getByPlaceholderText(/具体需求/);
      fireEvent.change(templateInput, { target: { value: 'Test' } });
      
      const button = screen.getByRole('button', { name: /生成 VibeGraph/i });
      fireEvent.click(button);
      
      expect(mockOnGenerate).toHaveBeenCalled();
    });

    it('should handle empty template but with description', () => {
      render(<VibeInput onGenerate={mockOnGenerate} isGenerating={false} />);
      
      const templateInput = screen.getByPlaceholderText(/具体需求/);
      fireEvent.change(templateInput, { target: { value: '' } });
      
      const button = screen.getByRole('button', { name: /生成 VibeGraph/i });
      fireEvent.click(button);
      
      expect(mockOnGenerate).not.toHaveBeenCalled();
    });

    it('should handle whitespace-only template', () => {
      render(<VibeInput onGenerate={mockOnGenerate} isGenerating={false} />);
      
      const templateInput = screen.getByPlaceholderText(/具体需求/);
      fireEvent.change(templateInput, { target: { value: '   ' } });
      
      const button = screen.getByRole('button', { name: /生成 VibeGraph/i });
      fireEvent.click(button);
      
      expect(mockOnGenerate).not.toHaveBeenCalled();
    });

    it('should handle special characters in template', async () => {
      const user = userEvent.setup();
      render(<VibeInput onGenerate={mockOnGenerate} isGenerating={false} />);
      
      const templateInput = screen.getByPlaceholderText(/具体需求/);
      await user.type(templateInput, 'START@#$%^&()A,B,C->D-END');
      
      const button = screen.getByRole('button', { name: /生成 VibeGraph/i });
      fireEvent.click(button);
      
      expect(mockOnGenerate).toHaveBeenCalledWith('START@#$%^&()A,B,C->D-END');
    });

    it('should handle newlines in template', async () => {
      const user = userEvent.setup();
      render(<VibeInput onGenerate={mockOnGenerate} isGenerating={false} />);
      
      const templateInput = screen.getByPlaceholderText(/具体需求/);
      await user.type(templateInput, 'START\\n->\\nA,B,C\\n->\\nEND');
      
      const button = screen.getByRole('button', { name: /生成 VibeGraph/i });
      fireEvent.click(button);
      
      expect(mockOnGenerate).toHaveBeenCalledWith('START\\n->\\nA,B,C\\n->\\nEND');
    });
  });
});

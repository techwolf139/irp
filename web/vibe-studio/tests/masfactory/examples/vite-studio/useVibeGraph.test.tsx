/**
 * VibeGraph Hook 测试
 * 测试状态管理和 API 调用
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useVibeGraph } from '../../../src/hooks/useVibeGraph';

// Mock fetch globally
const originalFetch = global.fetch;

describe('useVibeGraph Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    global.fetch = vi.fn();
  });

  afterEach(() => {
    global.fetch = originalFetch;
  });

  describe('initial state', () => {
    it('should initialize with empty user_intent', () => {
      const { result } = renderHook(() => useVibeGraph());
      
      expect(result.current.state.user_intent).toBe('');
    });

    it('should initialize with zero counts', () => {
      const { result } = renderHook(() => useVibeGraph());
      
      expect(result.current.state.node_count).toBe(0);
      expect(result.current.state.role_count).toBe(0);
    });

    it('should initialize with empty timestamps', () => {
      const { result } = renderHook(() => useVibeGraph());
      
      expect(result.current.state.generated_at).toBe('');
    });

    it('should initialize is_generating to false', () => {
      const { result } = renderHook(() => useVibeGraph());
      
      expect(result.current.state.is_generating).toBe(false);
    });

    it('should initialize with empty arrays', () => {
      const { result } = renderHook(() => useVibeGraph());
      
      expect(result.current.state.nodes).toEqual([]);
      expect(result.current.state.edges).toEqual([]);
    });
  });

  describe('generateGraph', () => {
    it('should set is_generating to true during API call', async () => {
      (global.fetch as Mock).mockResolvedValueOnce({
        ok: true,
        json: () => ({
          config: { nodes: [], edges: [] },
          metadata: { nodes_count: 0, edges_count: 0, roles: [] }
        })
      });
      
      const { result } = renderHook(() => useVibeGraph());
      
      await act(async () => {
        result.current.generateGraph({
          user_intent: 'Test workflow',
          topology_type: 'linear'
        });
      });
      
      expect(result.current.state.is_generating).toBe(true);
    });

    it('should update state with user_intent after generation', async () => {
      const mockResponse = {
        ok: true,
        json: () => ({
          config: {
            nodes: [{ id: 'node_1', type: 'Agent' }],
            edges: [{ source: 'entry', target: 'node_1' }]
          },
          metadata: {
            nodes_count: 1,
            edges_count: 1,
            roles: [{ role: 'approver' }]
          }
        })
      };
      
      (global.fetch as Mock).mockResolvedValueOnce(mockResponse);
      
      const { result } = renderHook(() => useVibeGraph());
      
      await act(async () => {
        await result.current.generateGraph({
          user_intent: 'Import workflow'
        });
      });
      
      expect(result.current.state.user_intent).toBe('Import workflow');
    });

    it('should update node_count and role_count from API response', async () => {
      const mockResponse = {
        ok: true,
        json: () => ({
          config: {
            nodes: [{ id: 'n1' }, { id: 'n2' }],
            edges: [{ source: 'n1', target: 'n2' }]
          },
          metadata: {
            nodes_count: 2,
            edges_count: 1,
            roles: [{ role: 'r1' }, { role: 'r2' }, { role: 'r3' }]
          }
        })
      };
      
      const { result } = renderHook(() => useVibeGraph());
      
      await act(async () => {
        await result.current.generateGraph({
          user_intent: 'Test',
          topology_type: 'linear'
        });
      });
      
      expect(result.current.state.node_count).toBe(2);
      expect(result.current.state.role_count).toBe(3);
    });

    it('should set generated_at timestamp after generation', async () => {
      const mockResponse = {
        ok: true,
        json: () => ({
          config: { nodes: [], edges: [] },
          metadata: { nodes_count: 0, edges_count: 0, roles: [] }
        })
      };
      
      (global.fetch as Mock).mockResolvedValueOnce(mockResponse);
      
      const { result } = renderHook(() => useVibeGraph());
      
      await act(async () => {
        await result.current.generateGraph({ user_intent: 'Test' });
      });
      
      expect(result.current.state.generated_at).not.toBe('');
      expect(new Date(result.current.state.generated_at)).toBeDefined();
    });

    it('should set is_generating to false after successful generation', async () => {
      const mockResponse = {
        ok: true,
        json: () => ({
          config: { nodes: [], edges: [] },
          metadata: { nodes_count: 0, edges_count: 0, roles: [] }
        })
      };
      
      (global.fetch as Mock).mockResolvedValueOnce(mockResponse);
      
      const { result } = renderHook(() => useVibeGraph());
      
      await act(async () => {
        await result.current.generateGraph({ user_intent: 'Test' });
      });
      
      expect(result.current.state.is_generating).toBe(false);
    });

    it('should update state with nodes from API response', async () => {
      const mockNodes = [
        { id: 'node_1', type: 'agent', data: { title: 'Test1' } },
        { id: 'node_2', type: 'agent', data: { title: 'Test2' } }
      ];
      
      const mockResponse = {
        ok: true,
        json: () => ({
          config: { nodes: mockNodes, edges: [] },
          metadata: { nodes_count: 2, edges_count: 0, roles: [] }
        })
      };
      
      (global.fetch as Mock).mockResolvedValueOnce(mockResponse);
      
      const { result } = renderHook(() => useVibeGraph());
      
      await act(async () => {
        await result.current.generateGraph({ user_intent: 'Test' });
      });
      
      expect(result.current.state.nodes).toEqual(mockNodes);
      expect(result.current.state.nodes.length).toBe(2);
    });

    it('should update state with edges from API response', async () => {
      const mockEdges = [
        { source: 'entry', target: 'node_1' },
        { source: 'node_1', target: 'node_2' }
      ];
      
      const mockResponse = {
        ok: true,
        json: () => ({
          config: { nodes: [], edges: mockEdges },
          metadata: { nodes_count: 0, edges_count: 2, roles: [] }
        })
      };
      
      (global.fetch as Mock).mockResolvedValueOnce(mockResponse);
      
      const { result } = renderHook(() => useVibeGraph());
      
      await act(async () => {
        await result.current.generateGraph({ user_intent: 'Test' });
      });
      
      expect(result.current.state.edges).toEqual(mockEdges);
      expect(result.current.state.edges.length).toBe(2);
    });
  });

  describe('reset', () => {
    it('should reset all state to initial values', async () => {
      const mockResponse = {
        ok: true,
        json: () => ({
          config: { nodes: [], edges: [] },
          metadata: { nodes_count: 1, edges_count: 0, roles: [] }
        })
      };
      
      (global.fetch as Mock).mockResolvedValueOnce(mockResponse);
      
      const { result } = renderHook(() => useVibeGraph());
      
      await act(async () => {
        await result.current.generateGraph({ user_intent: 'Test' });
      });
      
      expect(result.current.state.user_intent).toBe('Test');
      expect(result.current.state.node_count).toBe(1);
      
      act(() => {
        result.current.reset();
      });
      
      expect(result.current.state.user_intent).toBe('');
      expect(result.current.state.node_count).toBe(0);
      expect(result.current.state.role_count).toBe(0);
      expect(result.current.state.generated_at).toBe('');
      expect(result.current.state.is_generating).toBe(false);
      expect(result.current.state.nodes).toEqual([]);
      expect(result.current.state.edges).toEqual([]);
    });

    it('should clear error state on reset', async () => {
      (global.fetch as Mock).mockRejectedValueOnce(new Error('API failed'));
      
      const { result } = renderHook(() => useVibeGraph());
      
      await act(async () => {
        try {
          await result.current.generateGraph({ user_intent: 'Test' });
        } catch (e) {
          // Expected error
        }
      });
      
      // Reset should reset state to clean
      act(() => {
        result.current.reset();
      });
      
      expect(result.current.state.is_generating).toBe(false);
    });

    it('should reset properly after multiple generations', async () => {
      const { result } = renderHook(() => useVibeGraph());
      
      // First generation
      await act(async () => {
        await result.current.generateGraph({ user_intent: 'Test1' });
      });
      
      expect(result.current.state.user_intent).toBe('Test1');
      expect(result.current.state.node_count).toBe(0);
      
      // Reset
      act(() => {
        result.current.reset();
      });
      
      // Second generation
      await act(async () => {
        await result.current.generateGraph({ user_intent: 'Test2' });
      });
      
      expect(result.current.state.user_intent).toBe('Test2');
      expect(result.current.state.node_count).toBe(0);
    });
  });

  describe('error handling', () => {
    it('should handle network errors gracefully', async () => {
      (global.fetch as Mock).mockRejectedValueOnce(new Error('Network Error'));
      
      const consoleErrorSpy = vi.spyOn(console, 'error');
      const { result } = renderHook(() => useVibeGraph());
      
      await expect(
        result.current.generateGraph({ user_intent: 'Test' })
      ).rejects.toThrow();
      
      expect(consoleErrorSpy).toHaveBeenCalled();
      consoleErrorSpy.mockRestore();
    });

    it('should handle JSON parse errors', async () => {
      (global.fetch as Mock).mockResolvedValueOnce({
        ok: true,
        json: () => {
          throw new Error('Parse error');
        }
      });
      
      const consoleErrorSpy = vi.spyOn(console, 'error');
      const { result } = renderHook(() => useVibeGraph());
      
      await expect(
        result.current.generateGraph({ user_intent: 'Test' })
      ).rejects.toThrow();
      
      expect(consoleErrorSpy).toHaveBeenCalled();
      consoleErrorSpy.mockRestore();
    });

    it('should handle non-200 responses', async () => {
      (global.fetch as Mock).mockResolvedValueOnce({
        ok: false,
        status: 500
      });
      
      const consoleErrorSpy = vi.spyOn(console, 'error');
      const { result } = renderHook(() => useVibeGraph());
      
      await expect(
        result.current.generateGraph({ user_intent: 'Test' })
      ).rejects.toThrow();
      
      expect(consoleErrorSpy).toHaveBeenCalled();
      consoleErrorSpy.mockRestore();
    });
  });

  describe('edge cases', () => {
    it('should handle empty user_intent', async () => {
      const mockResponse = {
        ok: true,
        json: () => ({
          config: { nodes: [], edges: [] },
          metadata: { nodes_count: 0, edges_count: 0, roles: [] }
        })
      };
      
      (global.fetch as Mock).mockResolvedValueOnce(mockResponse);
      
      const { result } = renderHook(() => useVibeGraph());
      
      await act(async () => {
        await result.current.generateGraph({ user_intent: '' });
      });
      
      expect(result.current.state.user_intent).toBe('');
    });

    it('should handle very long user_intent', async () => {
      const longIntent = 'A'.repeat(10000);
      const mockResponse = {
        ok: true,
        json: () => ({
          config: { nodes: [], edges: [] },
          metadata: { nodes_count: 0, edges_count: 0, roles: [] }
        })
      };
      
      (global.fetch as Mock).mockResolvedValueOnce(mockResponse);
      
      const { result } = renderHook(() => useVibeGraph());
      
      await act(async () => {
        await result.current.generateGraph({ user_intent: longIntent });
      });
      
      expect(result.current.state.user_intent).toBe(longIntent);
    });

    it('should handle empty API response', async () => {
      const mockResponse = {
        ok: true,
        json: () => ({
          config: {},
          metadata: { nodes_count: 0, edges_count: 0, roles: [] }
        })
      };
      
      (global.fetch as Mock).mockResolvedValueOnce(mockResponse);
      
      const { result } = renderHook(() => useVibeGraph());
      
      await act(async () => {
        await result.current.generateGraph({ user_intent: 'Test' });
      });
      
      expect(result.current.state.nodes).toEqual([]);
      expect(result.current.state.edges).toEqual([]);
    });

    it('should handle special characters in user_intent', async () => {
      const specialIntent = '测试@#$%^&*()_+{}[]|\\:";\'<>?,./中文';
      const mockResponse = {
        ok: true,
        json: () => ({
          config: { nodes: [], edges: [] },
          metadata: { nodes_count: 0, edges_count: 0, roles: [] }
        })
      };
      
      (global.fetch as Mock).mockResolvedValueOnce(mockResponse);
      
      const { result } = renderHook(() => useVibeGraph());
      
      await act(async () => {
        await result.current.generateGraph({ user_intent: specialIntent });
      });
      
      expect(result.current.state.user_intent).toBe(specialIntent);
    });
  });

  describe('multiple simultaneous requests', () => {
    it('should handle concurrent generation requests', async () => {
      const mockResponses = [
        {
          ok: true,
          json: () => ({
            config: { nodes: [], edges: [] },
            metadata: { nodes_count: 1, edges_count: 0, roles: [] }
          })
        },
        {
          ok: true,
          json: () => ({
            config: { nodes: [], edges: [] },
            metadata: { nodes_count: 2, edges_count: 0, roles: [] }
          })
        }
      ];
      
      (global.fetch as Mock).mockResolvedValueOnce(mockResponses[0]).mockResolvedValueOnce(mockResponses[1]);
      
      const { result } = renderHook(() => useVibeGraph());
      
      const [first, second] = await Promise.all([
        act(async () => result.current.generateGraph({ user_intent: 'Test1' })),
        act(async () => result.current.generateGraph({ user_intent: 'Test2' }))
      ]);
      
      expect(result.current.state.user_intent).toBe('Test2');
      expect(result.current.state.node_count).toBe(2);
    });
  });
});

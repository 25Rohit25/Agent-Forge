import { Conversation, KnowledgeDoc, SearchResult, ServiceHealth, SystemOverview, ToolDefinition, Workflow } from '../types';

const API_BASE = 'http://localhost:8000/api';

export const api = {
  // Chat
  async sendMessage(message: string, conversationId?: string) {
    const res = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, conversation_id: conversationId }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Network error' }));
      throw new Error(err.detail || 'Failed to send message');
    }
    return res.json();
  },

  // Streaming SSE Chat
  streamChat(
    message: string,
    conversationId: string | undefined,
    onEvent: (event: string, data: any) => void,
    onError: (err: any) => void
  ) {
    const url = new URL(`${API_BASE}/chat/stream`);
    url.searchParams.set('message', message);
    if (conversationId) {
      url.searchParams.set('conversation_id', conversationId);
    }

    const eventSource = new EventSource(url.toString());

    eventSource.onmessage = (e) => {
      try {
        const parsed = JSON.parse(e.data);
        onEvent('message', parsed);
      } catch (err) {
        console.error('Error parsing SSE event:', err);
      }
    };

    const eventTypes = ['start', 'plan', 'tool_start', 'tool_complete', 'final_response', 'done'];
    eventTypes.forEach((type) => {
      eventSource.addEventListener(type, (e: any) => {
        try {
          const parsed = JSON.parse(e.data);
          onEvent(type, parsed);
          if (type === 'done') {
            eventSource.close();
          }
        } catch (err) {
          console.error(`Error in SSE ${type} event:`, err);
        }
      });
    });

    eventSource.onerror = (err) => {
      onError(err);
      eventSource.close();
    };

    return () => eventSource.close();
  },

  // Conversations
  async getConversations(): Promise<Conversation[]> {
    const res = await fetch(`${API_BASE}/conversations`);
    return res.ok ? res.json() : [];
  },

  async getConversation(id: string): Promise<Conversation | null> {
    const res = await fetch(`${API_BASE}/conversations/${id}`);
    return res.ok ? res.json() : null;
  },

  async deleteConversation(id: string): Promise<void> {
    await fetch(`${API_BASE}/conversations/${id}`, { method: 'DELETE' });
  },

  // Workflows
  async getWorkflows(): Promise<Workflow[]> {
    const res = await fetch(`${API_BASE}/workflows`);
    return res.ok ? res.json() : [];
  },

  async getWorkflow(id: string): Promise<Workflow | null> {
    const res = await fetch(`${API_BASE}/workflows/${id}`);
    return res.ok ? res.json() : null;
  },

  // Health
  async getServicesHealth(): Promise<SystemOverview> {
    const res = await fetch(`${API_BASE}/health/services`);
    if (!res.ok) throw new Error('Failed to fetch services telemetry');
    return res.json();
  },

  // Knowledge Base
  async getDocuments(): Promise<KnowledgeDoc[]> {
    const res = await fetch(`${API_BASE}/documents`);
    return res.ok ? res.json() : [];
  },

  async searchDocuments(query: string): Promise<{ results: SearchResult[] }> {
    const res = await fetch(`${API_BASE}/documents/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, limit: 4 }),
    });
    return res.ok ? res.json() : { results: [] };
  },

  // Tools
  async getTools(): Promise<ToolDefinition[]> {
    const res = await fetch(`${API_BASE}/tools`);
    return res.ok ? res.json() : [];
  },

  async executeTool(toolName: string, parameters: Record<string, any>) {
    const res = await fetch(`${API_BASE}/tools/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tool_name: toolName, parameters }),
    });
    return res.json();
  },
};

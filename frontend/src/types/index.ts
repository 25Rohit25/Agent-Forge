export interface ToolCallInfo {
  tool_name: string;
  arguments: Record<string, any>;
  output?: any;
  execution_time_ms: number;
  status: string;
}

export interface Message {
  id: string;
  role: 'USER' | 'ASSISTANT' | 'TOOL' | 'SYSTEM';
  content: string;
  tool_calls?: ToolCallInfo[];
  created_at?: string;
}

export interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  messages?: Message[];
}

export interface Workflow {
  id: string;
  conversation_id: string;
  request: string;
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED';
  steps_count: number;
  started_at: string;
  completed_at?: string;
  tool_executions?: ToolCallInfo[];
}

export interface ServiceHealth {
  name: string;
  display_name: string;
  status: 'healthy' | 'degraded' | 'critical' | 'unknown';
  error_rate: number;
  avg_latency_ms: number;
  p99_latency_ms: number;
  cpu_usage: number;
  memory_usage: number;
  active_instances: number;
  version: string;
  dependencies: string[];
}

export interface SystemOverview {
  overall_status: string;
  total_services: number;
  healthy_count: number;
  degraded_count: number;
  critical_count: number;
  avg_system_latency_ms: number;
  degraded_services: string[];
  critical_services: string[];
  services: ServiceHealth[];
}

export interface KnowledgeDoc {
  id: string;
  title: string;
  source: string;
  chunks_count?: number;
  created_at?: string;
}

export interface SearchResult {
  document_title: string;
  source: string;
  heading: string;
  chunk_index: number;
  score: number;
  content: string;
}

export interface ToolDefinition {
  name: string;
  description: string;
  category: string;
  parameters: {
    type: string;
    properties: Record<string, any>;
    required: string[];
  };
}

export interface StreamEvent {
  event: 'start' | 'plan' | 'tool_start' | 'tool_complete' | 'final_response' | 'done' | 'error';
  workflow_id?: string;
  data: any;
}

import React from 'react';
import {
  CheckCircle2,
  Clock,
  ChevronRight,
  Loader2,
  Activity,
  Search,
  BookOpen,
  Database,
  GitPullRequest,
  Send,
  Wrench,
  AlertCircle,
} from 'lucide-react';
import { ToolCallInfo } from '../../types';

interface WorkflowVisualizerProps {
  toolExecutions: ToolCallInfo[];
  isRunning: boolean;
  onInspectTool: (tool: ToolCallInfo) => void;
}

export const WorkflowVisualizer: React.FC<WorkflowVisualizerProps> = ({
  toolExecutions,
  isRunning,
  onInspectTool,
}) => {
  const getToolIcon = (name: string) => {
    switch (name) {
      case 'get_service_health':
        return Activity;
      case 'search_logs':
        return Search;
      case 'search_knowledge_base':
        return BookOpen;
      case 'query_database':
        return Database;
      case 'create_github_issue':
        return GitPullRequest;
      case 'send_slack_message':
        return Send;
      default:
        return Wrench;
    }
  };

  const getToolOutputSummary = (name: string, output: any) => {
    if (!output) return 'No output returned';
    if (name === 'get_service_health') {
      if (output.status) {
        return `Status: ${output.status.toUpperCase()} (Error: ${output.error_rate}%, Latency: ${output.avg_latency_ms}ms)`;
      }
      return `${output.total_services} services (${output.degraded_count} degraded)`;
    }
    if (name === 'search_logs') {
      return `${output.matches_count || 0} matching log lines found`;
    }
    if (name === 'search_knowledge_base') {
      return `${output.results_count || 0} runbook matches retrieved`;
    }
    if (name === 'query_database') {
      return `${output.records_count || 0} database records matched`;
    }
    if (name === 'create_github_issue') {
      return `GitHub Issue #${output.issue_number} created`;
    }
    if (name === 'send_slack_message') {
      return `Alert sent to ${output.channel}`;
    }
    return 'Completed';
  };

  return (
    <div className="w-80 border-l border-slate-200 bg-white flex flex-col h-[calc(100vh-3.5rem)] select-none">
      {/* Header */}
      <div className="p-3.5 border-b border-slate-200 flex items-center justify-between bg-slate-50/50">
        <div>
          <h2 className="text-xs font-semibold text-slate-900 tracking-tight">
            Agent Workflow Trace
          </h2>
          <p className="text-[10px] text-slate-500 font-mono">
            Structured Tool Execution Steps
          </p>
        </div>
        <div>
          {isRunning ? (
            <span className="flex items-center space-x-1.5 px-2 py-0.5 rounded-full bg-amber-50 text-amber-800 border border-amber-200 text-[10px] font-medium font-mono">
              <Loader2 className="w-3 h-3 animate-spin text-amber-600" />
              <span>RUNNING</span>
            </span>
          ) : toolExecutions.length > 0 ? (
            <span className="flex items-center space-x-1 px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200 text-[10px] font-medium font-mono">
              <CheckCircle2 className="w-3 h-3 text-emerald-600" />
              <span>{toolExecutions.length} STEPS</span>
            </span>
          ) : (
            <span className="text-[10px] text-slate-400 font-mono">IDLE</span>
          )}
        </div>
      </div>

      {/* Stepper Timeline */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2.5">
        {toolExecutions.length === 0 && !isRunning ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-6 text-slate-400 space-y-3">
            <div className="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center text-slate-400 border border-slate-200">
              <Wrench className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs font-medium text-slate-700">No Active Workflow</p>
              <p className="text-[11px] text-slate-400 mt-1 max-w-[200px]">
                Submit an engineering request to see the agent plan and execute tools in real time.
              </p>
            </div>
          </div>
        ) : (
          toolExecutions.map((step, idx) => {
            const Icon = getToolIcon(step.tool_name);
            const isSuccess = step.status === 'COMPLETED';

            return (
              <div
                key={idx}
                onClick={() => onInspectTool(step)}
                className="group relative p-2.5 rounded-lg border border-slate-200 hover:border-slate-300 hover:bg-slate-50/70 transition-all cursor-pointer shadow-subtle"
              >
                {/* Step header */}
                <div className="flex items-center justify-between mb-1.5">
                  <div className="flex items-center space-x-2">
                    <span className="w-4 h-4 rounded-full bg-slate-100 border border-slate-200 text-[10px] font-mono font-semibold flex items-center justify-center text-slate-600">
                      {idx + 1}
                    </span>
                    <div className="flex items-center space-x-1.5 font-mono text-xs font-semibold text-slate-900">
                      <Icon className="w-3.5 h-3.5 text-emerald-600" />
                      <span>{step.tool_name}</span>
                    </div>
                  </div>
                  <span className="flex items-center space-x-1 text-[10px] text-slate-400 font-mono">
                    <Clock className="w-2.5 h-2.5" />
                    <span>{step.execution_time_ms}ms</span>
                  </span>
                </div>

                {/* Output Summary */}
                <p className="text-[11px] text-slate-600 pl-6 leading-tight truncate">
                  {getToolOutputSummary(step.tool_name, step.output)}
                </p>

                {/* Hover inspect hint */}
                <div className="mt-2 pt-2 border-t border-slate-100 flex items-center justify-between text-[10px] text-slate-400 group-hover:text-emerald-700">
                  <span className="font-sans">Click to inspect payload</span>
                  <ChevronRight className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
                </div>
              </div>
            );
          })
        )}

        {isRunning && (
          <div className="p-3 rounded-lg border border-amber-200 bg-amber-50/50 flex items-center space-x-3 text-xs text-amber-800 animate-pulse">
            <Loader2 className="w-4 h-4 animate-spin text-amber-600" />
            <div className="font-mono text-[11px]">Agent executing next tool...</div>
          </div>
        )}
      </div>

      {/* Footer Info */}
      <div className="p-2.5 border-t border-slate-200 bg-slate-50/50 text-[10px] text-slate-400 text-center font-mono">
        All tool invocations sandboxed & logged
      </div>
    </div>
  );
};

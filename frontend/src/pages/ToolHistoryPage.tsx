import React, { useState, useEffect } from 'react';
import { Wrench, Play, Clock, CheckCircle2, AlertCircle, Copy, Check, Terminal } from 'lucide-react';
import { api } from '../services/api';
import { ToolDefinition } from '../types';

export const ToolHistoryPage: React.FC = () => {
  const [tools, setTools] = useState<ToolDefinition[]>([]);
  const [selectedTool, setSelectedTool] = useState<string>('get_service_health');
  const [paramInput, setParamInput] = useState<string>('{\n  "service_name": "payment-service"\n}');
  const [executionResult, setExecutionResult] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    loadTools();
  }, []);

  const loadTools = async () => {
    try {
      const data = await api.getTools();
      setTools(data);
    } catch (e) {
      console.error('Failed to load tools:', e);
    }
  };

  const handleToolSelect = (toolName: string) => {
    setSelectedTool(toolName);
    if (toolName === 'get_service_health') {
      setParamInput('{\n  "service_name": "payment-service"\n}');
    } else if (toolName === 'search_logs') {
      setParamInput('{\n  "service": "payment-service",\n  "level": "ERROR",\n  "max_lines": 10\n}');
    } else if (toolName === 'search_knowledge_base') {
      setParamInput('{\n  "query": "connection pool timeout",\n  "limit": 2\n}');
    } else if (toolName === 'query_database') {
      setParamInput('{\n  "query_type": "failed_transactions",\n  "service": "payment-service"\n}');
    } else if (toolName === 'create_github_issue') {
      setParamInput('{\n  "title": "Payment Service HikariCP Exhaustion",\n  "description": "50/50 pool capacity reached.",\n  "priority": "high",\n  "service": "payment-service"\n}');
    } else if (toolName === 'send_slack_message') {
      setParamInput('{\n  "channel": "#backend-alerts",\n  "message": "Payment service degraded.",\n  "severity": "warning"\n}');
    }
  };

  const handleExecute = async () => {
    setIsLoading(true);
    try {
      const parsed = JSON.parse(paramInput);
      const res = await api.executeTool(selectedTool, parsed);
      setExecutionResult(res);
    } catch (e: any) {
      setExecutionResult({
        status: 'FAILED',
        error: e.message || 'JSON Parse error in parameters'
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50/50">
      {/* Header */}
      <div>
        <h1 className="text-lg font-semibold text-slate-900 tracking-tight flex items-center space-x-2">
          <Wrench className="w-5 h-5 text-emerald-600" />
          <span>Engineering Tool Registry & Execution Sandbox</span>
        </h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Deterministic tool invocation testbed with parameter validation, execution timing, and JSON output inspection.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Tool Catalog */}
        <div className="space-y-3">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Available AI Tools ({tools.length})
          </h2>
          <div className="space-y-2">
            {tools.map((t) => {
              const isSelected = selectedTool === t.name;
              return (
                <div
                  key={t.name}
                  onClick={() => handleToolSelect(t.name)}
                  className={`p-3 rounded-xl border cursor-pointer transition-all ${
                    isSelected
                      ? 'border-emerald-500 bg-white shadow-subtle ring-1 ring-emerald-100'
                      : 'border-slate-200 bg-white hover:border-slate-300'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-mono text-xs font-bold text-slate-900">{t.name}()</span>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 font-mono">
                      {t.category}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500 leading-snug line-clamp-2">
                    {t.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column: Execution Sandbox */}
        <div className="lg:col-span-2 space-y-4">
          <div className="p-4 rounded-xl border border-slate-200 bg-white shadow-subtle space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xs font-semibold text-slate-900 flex items-center space-x-2">
                  <Terminal className="w-4 h-4 text-emerald-600" />
                  <span>Sandbox Invocation: {selectedTool}()</span>
                </h3>
                <p className="text-[11px] text-slate-500">Input parameter payload (JSON)</p>
              </div>

              <button
                onClick={handleExecute}
                disabled={isLoading}
                className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-200 text-white text-xs font-medium transition-colors shadow-sm"
              >
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>{isLoading ? 'Executing...' : 'Run Tool'}</span>
              </button>
            </div>

            <textarea
              rows={6}
              value={paramInput}
              onChange={(e) => setParamInput(e.target.value)}
              className="w-full p-3 font-mono text-xs bg-slate-900 text-slate-100 rounded-lg outline-none border border-slate-800 resize-y"
            />
          </div>

          {/* Results Block */}
          {executionResult && (
            <div className="p-4 rounded-xl border border-slate-200 bg-white shadow-subtle space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span
                    className={`px-2 py-0.5 rounded-full text-[10px] font-mono font-semibold uppercase ${
                      executionResult.status === 'COMPLETED'
                        ? 'bg-emerald-100 text-emerald-800'
                        : 'bg-red-100 text-red-800'
                    }`}
                  >
                    {executionResult.status}
                  </span>
                  <span className="flex items-center space-x-1 text-xs text-slate-500 font-mono">
                    <Clock className="w-3 h-3" />
                    <span>{executionResult.execution_time_ms} ms</span>
                  </span>
                </div>

                <button
                  onClick={() => {
                    navigator.clipboard.writeText(JSON.stringify(executionResult.output, null, 2));
                    setCopied(true);
                    setTimeout(() => setCopied(false), 2000);
                  }}
                  className="p-1.5 text-slate-500 hover:text-slate-900 rounded hover:bg-slate-100"
                  title="Copy result"
                >
                  {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                </button>
              </div>

              <pre className="p-3 font-mono text-[11px] bg-slate-900 text-slate-100 rounded-lg overflow-x-auto max-h-96 leading-relaxed border border-slate-800">
                {JSON.stringify(executionResult.output || executionResult.error, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

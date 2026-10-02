import React from 'react';
import { X, Copy, Check, Clock, Wrench } from 'lucide-react';
import { ToolCallInfo } from '../../types';

interface ToolExecutionDrawerProps {
  toolCall: ToolCallInfo | null;
  onClose: () => void;
}

export const ToolExecutionDrawer: React.FC<ToolExecutionDrawerProps> = ({
  toolCall,
  onClose,
}) => {
  const [copied, setCopied] = React.useState(false);

  if (!toolCall) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(
      JSON.stringify(
        {
          tool: toolCall.tool_name,
          input: toolCall.arguments,
          output: toolCall.output,
          duration_ms: toolCall.execution_time_ms,
        },
        null,
        2
      )
    );
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-y-0 right-0 w-96 bg-white border-l border-slate-200 shadow-premium z-50 flex flex-col animate-in slide-in-from-right duration-200">
      {/* Header */}
      <div className="p-4 border-b border-slate-200 flex items-center justify-between bg-slate-50/50">
        <div className="flex items-center space-x-2">
          <div className="p-1.5 rounded-md bg-emerald-50 text-emerald-700 border border-emerald-200">
            <Wrench className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-xs font-semibold font-mono text-slate-900">
              {toolCall.tool_name}()
            </h3>
            <div className="flex items-center space-x-2 text-[10px] text-slate-500 font-mono mt-0.5">
              <span className="flex items-center space-x-1">
                <Clock className="w-3 h-3" />
                <span>{toolCall.execution_time_ms}ms</span>
              </span>
              <span>•</span>
              <span
                className={`font-semibold ${
                  toolCall.status === 'COMPLETED' ? 'text-emerald-600' : 'text-amber-600'
                }`}
              >
                {toolCall.status}
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-1">
          <button
            onClick={handleCopy}
            className="p-1.5 text-slate-500 hover:text-slate-900 hover:bg-slate-100 rounded-md transition-colors"
            title="Copy JSON Payload"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
          </button>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-500 hover:text-slate-900 hover:bg-slate-100 rounded-md transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs font-mono">
        {/* Input Parameters */}
        <div>
          <label className="text-[11px] font-sans font-semibold text-slate-500 uppercase tracking-wider block mb-1.5">
            Input Arguments
          </label>
          <pre className="p-3 bg-slate-900 text-slate-100 rounded-lg overflow-x-auto text-[11px] leading-relaxed border border-slate-800">
            {JSON.stringify(toolCall.arguments, null, 2)}
          </pre>
        </div>

        {/* Output Results */}
        <div>
          <label className="text-[11px] font-sans font-semibold text-slate-500 uppercase tracking-wider block mb-1.5">
            Output Observation
          </label>
          <pre className="p-3 bg-slate-900 text-slate-100 rounded-lg overflow-x-auto text-[11px] leading-relaxed border border-slate-800 max-h-96">
            {JSON.stringify(toolCall.output, null, 2)}
          </pre>
        </div>
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-slate-200 bg-slate-50 text-[11px] text-slate-500 text-center font-sans">
        Agent Sandbox Execution Trace
      </div>
    </div>
  );
};

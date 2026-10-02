import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, Loader2, AlertTriangle, Terminal, Database, ShieldAlert } from 'lucide-react';
import { Message, ToolCallInfo } from '../../types';
import { MessageItem } from './MessageItem';

interface ChatBoxProps {
  messages: Message[];
  isLoading: boolean;
  onSendMessage: (text: string) => void;
  onInspectTool: (tool: ToolCallInfo) => void;
}

export const ChatBox: React.FC<ChatBoxProps> = ({
  messages,
  isLoading,
  onSendMessage,
  onInspectTool,
}) => {
  const [inputText, setInputText] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!inputText.trim() || isLoading) return;
    onSendMessage(inputText.trim());
    setInputText('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const sampleScenarios = [
    {
      title: 'Payment Latency Spike',
      query: 'Why is payment-service failing? Check the logs, search documentation, and open a GitHub issue.',
      icon: AlertTriangle,
      color: 'text-amber-600 bg-amber-50 border-amber-200'
    },
    {
      title: 'Checkout Cascading Errors',
      query: 'Investigate why checkout-service has latency spikes and cascading errors.',
      icon: Terminal,
      color: 'text-blue-600 bg-blue-50 border-blue-200'
    },
    {
      title: 'Database Pool Troubleshooting',
      query: 'What does our runbook say about payment database connection pool timeouts?',
      icon: Database,
      color: 'text-emerald-600 bg-emerald-50 border-emerald-200'
    },
    {
      title: 'Active Connections & Health',
      query: 'Check payment-service metrics, query database connection pools, inspect recent logs, and alert the team on Slack.',
      icon: ShieldAlert,
      color: 'text-indigo-600 bg-indigo-50 border-indigo-200'
    }
  ];

  return (
    <div className="flex-1 flex flex-col h-[calc(100vh-3.5rem)] bg-white overflow-hidden">
      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto">
        {messages.length === 0 ? (
          <div className="max-w-2xl mx-auto py-12 px-4 text-center space-y-6">
            <div className="inline-flex p-3 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-700 shadow-subtle">
              <Sparkles className="w-8 h-8" />
            </div>

            <div>
              <h2 className="text-xl font-semibold text-slate-900 tracking-tight">
                AgentForge AI Engineering Workspace
              </h2>
              <p className="text-xs text-slate-500 max-w-md mx-auto mt-1 leading-relaxed">
                Autonomous developer agent with live telemetry inspection, log grepping, RAG runbook retrieval, and automated GitHub ticketing.
              </p>
            </div>

            {/* Quick-Start Scenario Tiles */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-left pt-2">
              {sampleScenarios.map((sc, i) => {
                const Icon = sc.icon;
                return (
                  <button
                    key={i}
                    onClick={() => onSendMessage(sc.query)}
                    className="p-3.5 rounded-xl border border-slate-200 bg-white hover:border-slate-300 hover:shadow-subtle transition-all text-left group"
                  >
                    <div className="flex items-center space-x-2.5 mb-1.5">
                      <div className={`p-1.5 rounded-lg border ${sc.color}`}>
                        <Icon className="w-4 h-4" />
                      </div>
                      <span className="text-xs font-semibold text-slate-800 group-hover:text-emerald-700 transition-colors">
                        {sc.title}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-500 leading-snug line-clamp-2">
                      {sc.query}
                    </p>
                  </button>
                );
              })}
            </div>
          </div>
        ) : (
          <div>
            {messages.map((m) => (
              <MessageItem
                key={m.id}
                message={m}
                onInspectTool={onInspectTool}
              />
            ))}

            {isLoading && (
              <div className="p-4 flex items-center space-x-3 bg-slate-50/50 border-b border-slate-100">
                <div className="w-7 h-7 rounded-lg bg-emerald-600 flex items-center justify-center text-white shadow-sm font-mono text-xs">
                  <Loader2 className="w-4 h-4 animate-spin" />
                </div>
                <div className="flex items-center space-x-2 text-xs font-mono text-slate-600">
                  <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
                  <span>Agent is reasoning and gathering multi-source telemetry...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Box Footer */}
      <div className="p-3 border-t border-slate-200 bg-white/95 backdrop-blur-sm">
        <form
          onSubmit={handleSubmit}
          className="relative rounded-xl border border-slate-200 bg-slate-50/80 focus-within:bg-white focus-within:border-emerald-500 focus-within:ring-2 focus-within:ring-emerald-100 transition-all shadow-subtle p-2 flex items-end space-x-2"
        >
          <textarea
            ref={textareaRef}
            rows={1}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Instruct AgentForge: 'Investigate payment latency and open a GitHub issue...'"
            className="flex-1 bg-transparent resize-none outline-none text-xs text-slate-900 placeholder:text-slate-400 py-1.5 px-2 max-h-32"
          />

          <button
            type="submit"
            disabled={!inputText.trim() || isLoading}
            className="p-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-200 disabled:text-slate-400 text-white transition-colors shadow-sm shrink-0"
            title="Send prompt (Enter)"
          >
            {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
          </button>
        </form>

        <div className="flex items-center justify-between px-2 pt-1.5 text-[10px] text-slate-400 font-mono">
          <span>Shift + Enter for new line • Enter to submit</span>
          <span>FastAPI + PostgreSQL + pgvector + Redis</span>
        </div>
      </div>
    </div>
  );
};

import React from 'react';
import { X, Sparkles, AlertTriangle, ShieldCheck, Database, Server, ArrowRight } from 'lucide-react';

interface ScenarioModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectScenario: (prompt: string) => void;
}

export const ScenarioModal: React.FC<ScenarioModalProps> = ({
  isOpen,
  onClose,
  onSelectScenario,
}) => {
  if (!isOpen) return null;

  const scenarios = [
    {
      title: 'Payment Service Latency Spike (INC-001)',
      service: 'payment-service',
      tag: 'P1 Incident',
      tagColor: 'bg-red-50 text-red-700 border-red-200',
      icon: AlertTriangle,
      prompt:
        'Payment requests have become slow during the last hour. Investigate the issue, check logs and internal documentation, then create a GitHub issue if necessary.',
      description:
        'Triggers health check (870ms latency), discovers HikariCP ConnectionPoolTimeoutException in logs, matches payment runbook via RAG, and opens a GitHub issue.',
    },
    {
      title: 'Checkout Cascading Deadlock (INC-042)',
      service: 'checkout-service',
      tag: 'Cascading Failure',
      tagColor: 'bg-amber-50 text-amber-700 border-amber-200',
      icon: Server,
      prompt:
        'Investigate why checkout-service has latency spikes and cascading errors, check logs for deadlocks, and find related postmortems.',
      description:
        'Analyzes checkout cascading timeouts, queries inventory reservation deadlocks, and retrieves the INC-042 post-mortem.',
    },
    {
      title: 'Auth Service Security & Token Rotation',
      service: 'auth-service',
      tag: 'Security Audit',
      tagColor: 'bg-blue-50 text-blue-700 border-blue-200',
      icon: ShieldCheck,
      prompt:
        'Check auth-service health, inspect recent logs for token validation or rate limits, and summarize operational status.',
      description:
        'Validates that auth-service is healthy (42ms latency, 0.12% error), checks OAuth key rotation logs, and confirms operational stability.',
    },
    {
      title: 'Full Cluster Health & Slack Notification',
      service: 'all-services',
      tag: 'Observability',
      tagColor: 'bg-emerald-50 text-emerald-700 border-emerald-200',
      icon: Database,
      prompt:
        'Give me an overview of all active microservices in our cluster and alert the team on Slack if any are degraded.',
      description:
        'Scans all 6 microservices, flags payment-service and checkout-service as degraded, and delivers an alert to Slack #backend-alerts.',
    },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="w-full max-w-2xl bg-white rounded-2xl border border-slate-200 shadow-premium overflow-hidden">
        {/* Header */}
        <div className="p-4 border-b border-slate-200 flex items-center justify-between bg-slate-50/50">
          <div className="flex items-center space-x-2">
            <div className="p-1.5 rounded-lg bg-emerald-600 text-white shadow-sm">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-slate-900">
                Pre-Configured Engineering Scenarios
              </h2>
              <p className="text-[11px] text-slate-500">
                Select a scenario to watch AgentForge execute multi-step tool reasoning in real time
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-slate-700 rounded-md transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Scenarios List */}
        <div className="p-4 space-y-3 max-h-[70vh] overflow-y-auto">
          {scenarios.map((sc, i) => {
            const Icon = sc.icon;
            return (
              <div
                key={i}
                onClick={() => {
                  onSelectScenario(sc.prompt);
                  onClose();
                }}
                className="group p-3.5 rounded-xl border border-slate-200 hover:border-emerald-500 hover:bg-emerald-50/20 transition-all cursor-pointer shadow-subtle space-y-2"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Icon className="w-4 h-4 text-emerald-600" />
                    <span className="text-xs font-semibold text-slate-900 group-hover:text-emerald-800 transition-colors">
                      {sc.title}
                    </span>
                  </div>
                  <span
                    className={`text-[10px] font-mono px-2 py-0.5 rounded-full border ${sc.tagColor}`}
                  >
                    {sc.tag}
                  </span>
                </div>

                <p className="text-[11px] text-slate-600 leading-relaxed font-sans">
                  {sc.description}
                </p>

                <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px]">
                  <code className="text-[10px] font-mono text-slate-500 truncate max-w-md">
                    "{sc.prompt}"
                  </code>
                  <span className="text-emerald-700 font-medium flex items-center space-x-1 group-hover:translate-x-0.5 transition-transform">
                    <span>Launch</span>
                    <ArrowRight className="w-3 h-3" />
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Footer */}
        <div className="p-3 border-t border-slate-200 bg-slate-50 flex items-center justify-between text-[11px] text-slate-500">
          <span>Realistic portfolio demo workflows</span>
          <button
            onClick={onClose}
            className="px-3 py-1 bg-white border border-slate-200 hover:bg-slate-100 text-slate-700 rounded-md text-xs font-medium"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

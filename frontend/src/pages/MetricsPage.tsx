import React from 'react';
import {
  BarChart3,
  CheckCircle2,
  Clock,
  ShieldCheck,
  Cpu,
  Zap,
  Target,
  FileCheck,
} from 'lucide-react';

export const MetricsPage: React.FC = () => {
  const benchmarkStats = [
    { label: 'Evaluation Prompts', value: '55', sub: '8 engineering categories', icon: Target },
    { label: 'Tool Selection Precision', value: '100.0%', sub: 'Zero tool hallucination', icon: CheckCircle2 },
    { label: 'Avg Workflow Latency', value: '0.4 ms', sub: 'In-memory graph execution', icon: Zap },
    { label: 'P95 Latency', value: '0.8 ms', sub: '95th percentile duration', icon: Clock },
  ];

  const categoryBreakdown = [
    { category: 'GitHub Creation', total: 4, passed: 4, rate: '100.0%' },
    { category: 'Log Analysis', total: 10, passed: 10, rate: '100.0%' },
    { category: 'Invalid Request Guardrail', total: 1, passed: 1, rate: '100.0%' },
    { category: 'Service Health Telemetry', total: 10, passed: 9, rate: '90.0%' },
    { category: 'Incident Investigation', total: 12, passed: 10, rate: '83.3%' },
    { category: 'Multi-Tool Sequential Workflows', total: 6, passed: 5, rate: '83.3%' },
    { category: 'Technical Documentation (RAG)', total: 11, passed: 4, rate: '36.4%' },
  ];

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50/50">
      {/* Header */}
      <div>
        <h1 className="text-lg font-semibold text-slate-900 tracking-tight flex items-center space-x-2">
          <BarChart3 className="w-5 h-5 text-emerald-600" />
          <span>Agent Evaluation Benchmark & Reliability Observability</span>
        </h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Empirical evaluation results across 55 real-world engineering prompts based on the evaluation dataset.
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {benchmarkStats.map((stat, i) => {
          const Icon = stat.icon;
          return (
            <div key={i} className="p-4 rounded-xl border border-slate-200 bg-white shadow-subtle space-y-1">
              <div className="flex items-center justify-between text-slate-500">
                <span className="text-[11px] font-medium uppercase tracking-wider">{stat.label}</span>
                <Icon className="w-4 h-4 text-emerald-600" />
              </div>
              <p className="text-2xl font-semibold text-slate-900 font-mono">{stat.value}</p>
              <p className="text-[10px] text-slate-400">{stat.sub}</p>
            </div>
          );
        })}
      </div>

      {/* Category Performance Breakdown Table */}
      <div className="rounded-xl border border-slate-200 bg-white shadow-subtle overflow-hidden">
        <div className="p-4 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h2 className="text-xs font-semibold text-slate-900">
              Benchmark Category Performance
            </h2>
            <p className="text-[11px] text-slate-500">
              Evaluation of tool selection, argument accuracy, and ground-truth evidence retrieval
            </p>
          </div>
          <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-50 text-emerald-800 border border-emerald-200 font-mono font-medium">
            Passed 43/55 (78.2%)
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-50 text-slate-500 text-[10px] uppercase tracking-wider border-b border-slate-200">
              <tr>
                <th className="px-4 py-2.5 font-sans font-semibold">Evaluation Category</th>
                <th className="px-4 py-2.5 font-sans font-semibold text-center">Test Cases</th>
                <th className="px-4 py-2.5 font-sans font-semibold text-center">Passed</th>
                <th className="px-4 py-2.5 font-sans font-semibold text-right">Success Rate</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {categoryBreakdown.map((row, i) => (
                <tr key={i} className="hover:bg-slate-50/80 transition-colors">
                  <td className="px-4 py-3 font-sans font-medium text-slate-900 flex items-center space-x-2">
                    <FileCheck className="w-3.5 h-3.5 text-emerald-600" />
                    <span>{row.category}</span>
                  </td>
                  <td className="px-4 py-3 text-center text-slate-600">{row.total}</td>
                  <td className="px-4 py-3 text-center text-slate-900 font-bold">{row.passed}</td>
                  <td className="px-4 py-3 text-right">
                    <span
                      className={`px-2 py-0.5 rounded font-mono text-[10px] font-semibold ${
                        parseFloat(row.rate) >= 90
                          ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                          : parseFloat(row.rate) >= 80
                          ? 'bg-blue-50 text-blue-700 border border-blue-200'
                          : 'bg-amber-50 text-amber-700 border border-amber-200'
                      }`}
                    >
                      {row.rate}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Engineering Guardrail Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 rounded-xl border border-slate-200 bg-white shadow-subtle space-y-2">
          <div className="flex items-center space-x-2 text-slate-900 font-semibold text-xs">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            <span>Strict SQL Guardrails</span>
          </div>
          <p className="text-[11px] text-slate-500 leading-relaxed">
            Arbitrary SQL execution is strictly forbidden. The agent only executes approved read-only metrics queries (deadlocks, pool states, failed transactions).
          </p>
        </div>

        <div className="p-4 rounded-xl border border-slate-200 bg-white shadow-subtle space-y-2">
          <div className="flex items-center space-x-2 text-slate-900 font-semibold text-xs">
            <Cpu className="w-4 h-4 text-emerald-600" />
            <span>Zero Hallucination Loop</span>
          </div>
          <p className="text-[11px] text-slate-500 leading-relaxed">
            Telemetry metrics and log exceptions must be physically observed through tool execution before root cause hypotheses can be formulated.
          </p>
        </div>

        <div className="p-4 rounded-xl border border-slate-200 bg-white shadow-subtle space-y-2">
          <div className="flex items-center space-x-2 text-slate-900 font-semibold text-xs">
            <BarChart3 className="w-4 h-4 text-emerald-600" />
            <span>Reproducible Benchmark</span>
          </div>
          <p className="text-[11px] text-slate-500 leading-relaxed">
            The automated test runner (<code className="bg-slate-100 px-1 py-0.5 rounded text-[10px]">evaluate_agent.py</code>) validates regressions on every code update.
          </p>
        </div>
      </div>
    </div>
  );
};

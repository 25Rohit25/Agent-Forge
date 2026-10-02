import React from 'react';
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Cpu,
  Layers,
  Server,
  Sparkles,
  ArrowUpRight,
  RefreshCw,
} from 'lucide-react';
import { SystemOverview, ServiceHealth } from '../types';

interface HealthDashboardProps {
  overview?: SystemOverview | null;
  onRefresh: () => void;
  onLaunchInvestigation: (serviceName: string) => void;
}

export const HealthDashboard: React.FC<HealthDashboardProps> = ({
  overview,
  onRefresh,
  onLaunchInvestigation,
}) => {
  if (!overview) {
    return (
      <div className="flex-1 flex items-center justify-center p-12 text-slate-400">
        <RefreshCw className="w-5 h-5 animate-spin mr-2" />
        <span>Loading microservice telemetry...</span>
      </div>
    );
  }

  const { services, total_services, healthy_count, degraded_count, critical_count, avg_system_latency_ms } = overview;

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50/50">
      {/* Top Banner & High-level Metrics */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-lg font-semibold text-slate-900 tracking-tight flex items-center space-x-2">
            <span>Cluster Services & Telemetry Monitor</span>
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-mono">
              Live Prometheus Simulator
            </span>
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Real-time observability across {total_services} production microservices.
          </p>
        </div>

        <button
          onClick={onRefresh}
          className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-xs font-medium shadow-subtle transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Telemetry</span>
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="p-4 rounded-xl border border-slate-200 bg-white shadow-subtle">
          <span className="text-[11px] font-medium text-slate-500 uppercase tracking-wider">Total Services</span>
          <p className="text-2xl font-semibold text-slate-900 mt-1 font-mono">{total_services}</p>
          <span className="text-[10px] text-slate-400">All registered in mesh</span>
        </div>

        <div className="p-4 rounded-xl border border-emerald-200 bg-emerald-50/30 shadow-subtle">
          <span className="text-[11px] font-medium text-emerald-700 uppercase tracking-wider">Healthy</span>
          <p className="text-2xl font-semibold text-emerald-800 mt-1 font-mono">{healthy_count}</p>
          <span className="text-[10px] text-emerald-600">Within latency SLOs</span>
        </div>

        <div className="p-4 rounded-xl border border-amber-200 bg-amber-50/30 shadow-subtle">
          <span className="text-[11px] font-medium text-amber-700 uppercase tracking-wider">Degraded</span>
          <p className="text-2xl font-semibold text-amber-800 mt-1 font-mono">{degraded_count}</p>
          <span className="text-[10px] text-amber-600">Error rate {'>'} 5.0%</span>
        </div>

        <div className="p-4 rounded-xl border border-slate-200 bg-white shadow-subtle">
          <span className="text-[11px] font-medium text-slate-500 uppercase tracking-wider">Avg Cluster Latency</span>
          <p className="text-2xl font-semibold text-slate-900 mt-1 font-mono">{avg_system_latency_ms} ms</p>
          <span className="text-[10px] text-slate-400">P99 max: 2400 ms</span>
        </div>
      </div>

      {/* Services Grid */}
      <div className="space-y-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-500">
          Microservices Inventory
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {services.map((svc) => {
            const isDegraded = svc.status === 'degraded';
            return (
              <div
                key={svc.name}
                className={`p-4 rounded-xl border transition-all shadow-subtle bg-white ${
                  isDegraded
                    ? 'border-amber-300 hover:border-amber-400 ring-1 ring-amber-100'
                    : 'border-slate-200 hover:border-slate-300'
                }`}
              >
                {/* Header */}
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="text-xs font-bold text-slate-900 font-mono">
                      {svc.name}
                    </h3>
                    <p className="text-[11px] text-slate-500">{svc.display_name}</p>
                  </div>
                  <span
                    className={`px-2 py-0.5 rounded-full text-[10px] font-mono font-semibold uppercase ${
                      isDegraded
                        ? 'bg-amber-100 text-amber-800 border border-amber-200'
                        : 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                    }`}
                  >
                    {svc.status}
                  </span>
                </div>

                {/* Metrics */}
                <div className="grid grid-cols-2 gap-2 p-2 rounded-lg bg-slate-50 border border-slate-100 font-mono text-[11px] mb-3">
                  <div>
                    <span className="text-slate-400 text-[10px] block">Error Rate</span>
                    <span className={isDegraded ? 'text-amber-700 font-bold' : 'text-slate-700'}>
                      {svc.error_rate}%
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 text-[10px] block">Avg Latency</span>
                    <span className={isDegraded ? 'text-amber-700 font-bold' : 'text-slate-700'}>
                      {svc.avg_latency_ms} ms
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 text-[10px] block">CPU Usage</span>
                    <span className="text-slate-700">{svc.cpu_usage}%</span>
                  </div>
                  <div>
                    <span className="text-slate-400 text-[10px] block">Pod Replicas</span>
                    <span className="text-slate-700">{svc.active_instances} instances</span>
                  </div>
                </div>

                {/* Dependencies */}
                <div className="mb-3">
                  <span className="text-[10px] text-slate-400 block mb-1">Dependencies:</span>
                  <div className="flex flex-wrap gap-1">
                    {svc.dependencies.map((dep, idx) => (
                      <span
                        key={idx}
                        className="px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 text-[10px] font-mono"
                      >
                        {dep}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Action Trigger */}
                <button
                  onClick={() => onLaunchInvestigation(svc.name)}
                  className="w-full flex items-center justify-center space-x-1.5 py-1.5 px-3 rounded-lg border border-slate-200 hover:border-emerald-500 hover:bg-emerald-50/50 text-slate-700 hover:text-emerald-800 text-xs font-medium transition-colors"
                >
                  <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
                  <span>Diagnose with Agent</span>
                  <ArrowUpRight className="w-3.5 h-3.5" />
                </button>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

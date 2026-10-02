import React from 'react';
import { Activity, ShieldAlert, Cpu, Terminal, RefreshCw, UserCheck } from 'lucide-react';
import { SystemOverview } from '../../types';

interface NavbarProps {
  overview?: SystemOverview | null;
  onRefreshHealth?: () => void;
  onOpenScenarioModal?: () => void;
  activeTab: string;
}

export const Navbar: React.FC<NavbarProps> = ({
  overview,
  onRefreshHealth,
  onOpenScenarioModal,
  activeTab
}) => {
  const isDegraded = overview && overview.degraded_count > 0;

  return (
    <header className="h-14 border-b border-slate-200 bg-white/95 backdrop-blur-md px-4 flex items-center justify-between sticky top-0 z-30 shadow-subtle">
      {/* Brand & System Status */}
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-emerald-600 flex items-center justify-center text-white shadow-sm font-mono font-bold text-sm tracking-wider">
            AF
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-semibold text-slate-900 text-sm tracking-tight">AgentForge</span>
              <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200 font-medium">
                Workspace
              </span>
            </div>
          </div>
        </div>

        <div className="h-4 w-px bg-slate-200" />

        {/* Live Cluster Status Badge */}
        <div className="flex items-center space-x-2">
          {isDegraded ? (
            <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-amber-50 border border-amber-200 text-amber-800 text-xs font-medium">
              <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
              <span>{overview?.degraded_count} Service Degraded</span>
            </div>
          ) : (
            <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-medium">
              <span className="w-2 h-2 rounded-full bg-emerald-500" />
              <span>All Systems Operational</span>
            </div>
          )}
        </div>
      </div>

      {/* Model & Operational Controls */}
      <div className="flex items-center space-x-3">
        {/* Model Indicator */}
        <div className="hidden md:flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-slate-50 border border-slate-200 text-slate-600 text-xs font-mono">
          <Cpu className="w-3.5 h-3.5 text-emerald-600" />
          <span>gpt-4o-mini (Agentic)</span>
        </div>

        {/* Quick Incident Scenario Trigger */}
        <button
          onClick={onOpenScenarioModal}
          className="inline-flex items-center space-x-1.5 px-2.5 py-1 text-xs font-medium text-slate-700 bg-white hover:bg-slate-50 border border-slate-200 rounded-md transition-colors shadow-subtle"
          title="Launch pre-configured engineering incident scenarios"
        >
          <Terminal className="w-3.5 h-3.5 text-slate-600" />
          <span>Quick Scenarios</span>
        </button>

        {/* Refresh health button */}
        {onRefreshHealth && (
          <button
            onClick={onRefreshHealth}
            className="p-1.5 text-slate-500 hover:text-slate-900 hover:bg-slate-100 rounded-md transition-colors"
            title="Refresh cluster telemetry"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        )}

        <div className="h-4 w-px bg-slate-200" />

        {/* User Profile */}
        <div className="flex items-center space-x-2 pl-1">
          <div className="w-7 h-7 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-700 text-xs font-medium">
            RS
          </div>
          <div className="hidden lg:block text-left">
            <p className="text-xs font-medium text-slate-900 leading-tight">Rohit Singh</p>
            <p className="text-[10px] text-slate-500 font-mono">Staff Reliability</p>
          </div>
        </div>
      </div>
    </header>
  );
};

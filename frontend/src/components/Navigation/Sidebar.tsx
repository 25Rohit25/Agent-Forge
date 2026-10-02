import React from 'react';
import {
  MessageSquare,
  Activity,
  BookOpen,
  Wrench,
  BarChart3,
  Plus,
  Trash2,
  Clock,
  Sparkles,
} from 'lucide-react';
import { Conversation } from '../../types';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  conversations: Conversation[];
  activeConversationId?: string;
  onSelectConversation: (id: string) => void;
  onNewConversation: () => void;
  onDeleteConversation: (id: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  setActiveTab,
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewConversation,
  onDeleteConversation,
}) => {
  const navItems = [
    { id: 'workspace', label: 'AI Workspace', icon: MessageSquare, badge: null },
    { id: 'health', label: 'Service Health', icon: Activity, badge: 'Live' },
    { id: 'knowledge', label: 'Knowledge Base', icon: BookOpen, badge: 'RAG' },
    { id: 'tools', label: 'Tool Sandbox', icon: Wrench, badge: '6 Tools' },
    { id: 'metrics', label: 'Benchmarks', icon: BarChart3, badge: '55 Tests' },
  ];

  return (
    <aside className="w-64 border-r border-slate-200 bg-slate-50/70 flex flex-col h-[calc(100vh-3.5rem)] select-none">
      {/* Primary Navigation */}
      <div className="p-3 space-y-1">
        <button
          onClick={onNewConversation}
          className="w-full flex items-center justify-center space-x-2 px-3 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg font-medium text-xs shadow-sm transition-colors mb-3"
        >
          <Plus className="w-4 h-4" />
          <span>New Investigation</span>
        </button>

        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                isActive
                  ? 'bg-white text-slate-900 shadow-subtle border border-slate-200'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100/80'
              }`}
            >
              <div className="flex items-center space-x-2.5">
                <Icon
                  className={`w-4 h-4 ${
                    isActive ? 'text-emerald-600' : 'text-slate-500'
                  }`}
                />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span
                  className={`text-[10px] px-1.5 py-0.5 rounded-full font-mono font-medium ${
                    item.badge === 'Live'
                      ? 'bg-amber-100 text-amber-800 border border-amber-200'
                      : 'bg-slate-100 text-slate-600 border border-slate-200'
                  }`}
                >
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      <div className="px-4 py-2 border-t border-slate-200">
        <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
          Recent Investigations
        </span>
      </div>

      {/* Recent Investigations List */}
      <div className="flex-1 overflow-y-auto px-2 space-y-0.5">
        {conversations.length === 0 ? (
          <div className="p-4 text-center text-xs text-slate-400 italic">
            No past investigations yet. Launch one from the workspace.
          </div>
        ) : (
          conversations.map((c) => {
            const isSelected = activeConversationId === c.id;
            return (
              <div
                key={c.id}
                onClick={() => {
                  onSelectConversation(c.id);
                  setActiveTab('workspace');
                }}
                className={`group flex items-center justify-between px-2.5 py-1.5 rounded-md text-xs cursor-pointer transition-colors ${
                  isSelected
                    ? 'bg-white text-slate-900 font-medium border border-slate-200 shadow-subtle'
                    : 'text-slate-600 hover:bg-slate-100/70 hover:text-slate-900'
                }`}
              >
                <div className="flex items-center space-x-2 overflow-hidden pr-1">
                  <Clock className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                  <span className="truncate">{c.title || 'Investigation Run'}</span>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteConversation(c.id);
                  }}
                  className="opacity-0 group-hover:opacity-100 p-1 text-slate-400 hover:text-red-600 transition-opacity"
                  title="Delete investigation"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </div>
            );
          })
        )}
      </div>

      {/* Footer Info */}
      <div className="p-3 border-t border-slate-200 bg-white/50 text-[11px] text-slate-500 flex items-center justify-between">
        <div className="flex items-center space-x-1.5 font-mono">
          <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
          <span>v1.0.0 Production</span>
        </div>
        <span className="text-slate-400">FastAPI + RAG</span>
      </div>
    </aside>
  );
};

import React from 'react';
import { User, Bot, Wrench, CheckCircle, Copy, Check } from 'lucide-react';
import { Message, ToolCallInfo } from '../../types';

interface MessageItemProps {
  message: Message;
  onInspectTool?: (tool: ToolCallInfo) => void;
}

export const MessageItem: React.FC<MessageItemProps> = ({ message, onInspectTool }) => {
  const isUser = message.role === 'USER';
  const [copied, setCopied] = React.useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Simple clean markdown formatter
  const renderFormattedContent = (content: string) => {
    const lines = content.split('\n');
    return lines.map((line, idx) => {
      // Headers
      if (line.startsWith('### ')) {
        return (
          <h3 key={idx} className="text-sm font-semibold text-slate-900 mt-4 mb-1.5 flex items-center space-x-2">
            <span>{line.replace('### ', '')}</span>
          </h3>
        );
      }
      if (line.startsWith('#### ')) {
        return (
          <h4 key={idx} className="text-xs font-semibold uppercase tracking-wider text-slate-700 mt-3 mb-1">
            {line.replace('#### ', '')}
          </h4>
        );
      }
      // Bullets
      if (line.startsWith('- ') || line.startsWith('* ')) {
        const text = line.substring(2);
        return (
          <div key={idx} className="flex items-start space-x-2 text-xs text-slate-700 my-0.5 leading-relaxed">
            <span className="text-slate-400 mt-0.5">•</span>
            <span>{formatInlineMarkdown(text)}</span>
          </div>
        );
      }
      // Code blocks
      if (line.startsWith('```')) {
        return null;
      }
      // Divider
      if (line.trim() === '---') {
        return <hr key={idx} className="my-3 border-slate-200" />;
      }
      // Normal paragraph
      if (!line.trim()) {
        return <div key={idx} className="h-2" />;
      }
      return (
        <p key={idx} className="text-xs text-slate-700 leading-relaxed my-0.5">
          {formatInlineMarkdown(line)}
        </p>
      );
    });
  };

  const formatInlineMarkdown = (text: string) => {
    // Bold **text**
    const parts = text.split(/(\*\*.*?\*\*|`.*?`|\[.*?\]\(.*?\))/g);
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i} className="font-semibold text-slate-900">{part.slice(2, -2)}</strong>;
      }
      if (part.startsWith('`') && part.endsWith('`')) {
        return (
          <code key={i} className="px-1 py-0.5 rounded bg-slate-100 border border-slate-200 font-mono text-[11px] text-slate-800">
            {part.slice(1, -1)}
          </code>
        );
      }
      if (part.startsWith('[') && part.includes('](') && part.endsWith(')')) {
        const match = part.match(/\[(.*?)\]\((.*?)\)/);
        if (match) {
          return (
            <a
              key={i}
              href={match[2]}
              target="_blank"
              rel="noreferrer"
              className="text-emerald-700 hover:text-emerald-800 underline font-medium"
            >
              {match[1]}
            </a>
          );
        }
      }
      return part;
    });
  };

  return (
    <div
      className={`p-4 flex space-x-3.5 transition-colors ${
        isUser ? 'bg-slate-50/60 border-b border-slate-100' : 'bg-white border-b border-slate-200'
      }`}
    >
      {/* Avatar */}
      <div className="shrink-0 mt-0.5">
        {isUser ? (
          <div className="w-7 h-7 rounded-lg bg-slate-200 flex items-center justify-center text-slate-700 shadow-sm">
            <User className="w-4 h-4" />
          </div>
        ) : (
          <div className="w-7 h-7 rounded-lg bg-emerald-600 flex items-center justify-center text-white shadow-sm font-mono font-bold text-xs">
            <Bot className="w-4 h-4" />
          </div>
        )}
      </div>

      {/* Message Content */}
      <div className="flex-1 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between mb-1.5">
          <div className="flex items-center space-x-2">
            <span className="text-xs font-semibold text-slate-900">
              {isUser ? 'You (Staff SRE)' : 'AgentForge Autonomous Agent'}
            </span>
            {!isUser && (
              <span className="text-[10px] px-1.5 py-0.2 rounded bg-emerald-50 text-emerald-700 border border-emerald-200 font-mono">
                Reasoning Model
              </span>
            )}
          </div>
          <button
            onClick={handleCopy}
            className="p-1 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded transition-colors"
            title="Copy message"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
          </button>
        </div>

        {/* Tools badges if any */}
        {message.tool_calls && message.tool_calls.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mb-3 mt-1">
            {message.tool_calls.map((tool, idx) => (
              <button
                key={idx}
                onClick={() => onInspectTool && onInspectTool(tool)}
                className="inline-flex items-center space-x-1.5 px-2 py-0.5 rounded-md bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200 font-mono text-[10px] transition-colors"
              >
                <Wrench className="w-3 h-3 text-emerald-600" />
                <span>{tool.tool_name}()</span>
                <span className="text-slate-400 text-[9px]">{tool.execution_time_ms}ms</span>
              </button>
            ))}
          </div>
        )}

        {/* Formatted body */}
        <div className="space-y-1">
          {renderFormattedContent(message.content)}
        </div>
      </div>
    </div>
  );
};

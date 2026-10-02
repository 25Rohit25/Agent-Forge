import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navigation/Navbar';
import { Sidebar } from './components/Navigation/Sidebar';
import { ChatBox } from './components/Chat/ChatBox';
import { WorkflowVisualizer } from './components/Workflow/WorkflowVisualizer';
import { ToolExecutionDrawer } from './components/Workflow/ToolExecutionDrawer';
import { ScenarioModal } from './components/Modals/ScenarioModal';
import { HealthDashboard } from './pages/HealthDashboard';
import { KnowledgeBasePage } from './pages/KnowledgeBasePage';
import { ToolHistoryPage } from './pages/ToolHistoryPage';
import { MetricsPage } from './pages/MetricsPage';
import { api } from './services/api';
import { Conversation, Message, SystemOverview, ToolCallInfo } from './types';

export function App() {
  const [activeTab, setActiveTab] = useState<string>('workspace');
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConvId, setCurrentConvId] = useState<string | undefined>(undefined);
  const [messages, setMessages] = useState<Message[]>([]);
  const [toolExecutions, setToolExecutions] = useState<ToolCallInfo[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [overview, setOverview] = useState<SystemOverview | null>(null);
  const [inspectedTool, setInspectedTool] = useState<ToolCallInfo | null>(null);
  const [isScenarioModalOpen, setIsScenarioModalOpen] = useState<boolean>(false);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const [convs, health] = await Promise.all([
        api.getConversations().catch(() => []),
        api.getServicesHealth().catch(() => null),
      ]);
      setConversations(convs);
      setOverview(health);
    } catch (e) {
      console.error('Error loading initial data:', e);
    }
  };

  const refreshHealth = async () => {
    try {
      const health = await api.getServicesHealth();
      setOverview(health);
    } catch (e) {
      console.error('Failed to refresh health:', e);
    }
  };

  const handleSelectConversation = async (id: string) => {
    setCurrentConvId(id);
    try {
      const conv = await api.getConversation(id);
      if (conv) {
        setMessages(conv.messages || []);
        // Extract tool calls from last assistant message if available
        const lastAsst = conv.messages?.slice().reverse().find((m) => m.role === 'ASSISTANT');
        if (lastAsst && lastAsst.tool_calls) {
          setToolExecutions(lastAsst.tool_calls);
        } else {
          setToolExecutions([]);
        }
      }
    } catch (e) {
      console.error('Failed to load conversation:', e);
    }
  };

  const handleNewConversation = () => {
    setCurrentConvId(undefined);
    setMessages([]);
    setToolExecutions([]);
    setActiveTab('workspace');
  };

  const handleDeleteConversation = async (id: string) => {
    try {
      await api.deleteConversation(id);
      setConversations((prev) => prev.filter((c) => c.id !== id));
      if (currentConvId === id) {
        handleNewConversation();
      }
    } catch (e) {
      console.error('Failed to delete conversation:', e);
    }
  };

  const handleSendMessage = async (text: string) => {
    if (!text.trim() || isLoading) return;

    const userMessage: Message = {
      id: `msg_${Date.now()}`,
      role: 'USER',
      content: text,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setToolExecutions([]);

    try {
      const resp = await api.sendMessage(text, currentConvId);
      setCurrentConvId(resp.conversation_id);

      const assistantMessage: Message = {
        id: `asst_${Date.now()}`,
        role: 'ASSISTANT',
        content: resp.response,
        tool_calls: resp.tool_executions || [],
        created_at: resp.created_at || new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setToolExecutions(resp.tool_executions || []);

      // Refresh conversations list and telemetry
      const updatedConvs = await api.getConversations();
      setConversations(updatedConvs);
      refreshHealth();
    } catch (err: any) {
      console.error('Error in agent execution:', err);
      const errorMessage: Message = {
        id: `err_${Date.now()}`,
        role: 'ASSISTANT',
        content: `### Execution Error\n\nFailed to complete agent workflow: ${err.message || 'Unknown network error'}. Please verify backend is running.`,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLaunchInvestigation = (serviceName: string) => {
    const prompt = `Investigate why ${serviceName} is degraded, check logs for errors, search our runbooks, and file a GitHub issue if error rate exceeds 5%.`;
    setActiveTab('workspace');
    handleSendMessage(prompt);
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col antialiased">
      {/* Top Navbar */}
      <Navbar
        overview={overview}
        onRefreshHealth={refreshHealth}
        onOpenScenarioModal={() => setIsScenarioModalOpen(true)}
        activeTab={activeTab}
      />

      {/* Main Workspace Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar */}
        <Sidebar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          conversations={conversations}
          activeConversationId={currentConvId}
          onSelectConversation={handleSelectConversation}
          onNewConversation={handleNewConversation}
          onDeleteConversation={handleDeleteConversation}
        />

        {/* Center Active Workspace / Dashboard Tab */}
        {activeTab === 'workspace' && (
          <main className="flex-1 flex overflow-hidden">
            <ChatBox
              messages={messages}
              isLoading={isLoading}
              onSendMessage={handleSendMessage}
              onInspectTool={(tool) => setInspectedTool(tool)}
            />

            {/* Right Workflow Stepper */}
            <WorkflowVisualizer
              toolExecutions={toolExecutions}
              isRunning={isLoading}
              onInspectTool={(tool) => setInspectedTool(tool)}
            />
          </main>
        )}

        {activeTab === 'health' && (
          <HealthDashboard
            overview={overview}
            onRefresh={refreshHealth}
            onLaunchInvestigation={handleLaunchInvestigation}
          />
        )}

        {activeTab === 'knowledge' && <KnowledgeBasePage />}

        {activeTab === 'tools' && <ToolHistoryPage />}

        {activeTab === 'metrics' && <MetricsPage />}
      </div>

      {/* Tool Execution Drawer */}
      <ToolExecutionDrawer
        toolCall={inspectedTool}
        onClose={() => setInspectedTool(null)}
      />

      {/* Scenario Launch Modal */}
      <ScenarioModal
        isOpen={isScenarioModalOpen}
        onClose={() => setIsScenarioModalOpen(false)}
        onSelectScenario={(prompt) => {
          setActiveTab('workspace');
          handleSendMessage(prompt);
        }}
      />
    </div>
  );
}

export default App;

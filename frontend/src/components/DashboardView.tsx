import { Sidebar } from './Sidebar';
import { Dashboard } from './Dashboard';
import { UnifiedChatbotPanel } from './UnifiedChatbotPanel';
import { TopMenuBar } from './TopMenuBar';
import { useState } from 'react';

interface DashboardViewProps {
  currentView?: string;
  onViewChange?: (view: string) => void;
  onShowImportModal?: () => void;
}

export function DashboardView({ currentView, onViewChange, onShowImportModal }: DashboardViewProps) {
  const [showAIAssistant, setShowAIAssistant] = useState(false);
  return (
    <div className="flex flex-col h-screen">
      {/* Menu supérieur type VSCode */}
      <TopMenuBar 
        currentView={currentView} 
        onViewChange={onViewChange}
        onShowImportModal={onShowImportModal}
      />
      
      <div className="flex flex-1 overflow-hidden">
        {/* Barre latérale gauche */}
        <Sidebar activeView="dashboard" onNavigate={onViewChange} onToggleAI={() => setShowAIAssistant(!showAIAssistant)} />

        {/* Zone centrale - Dashboard */}
        <Dashboard />

        {/* Zone réservée pour les composants futurs */}

        {/* Panneau latéral droit - Assistant IA */}
        {showAIAssistant && <UnifiedChatbotPanel type="ai" />}
      </div>
    </div>
  );
}
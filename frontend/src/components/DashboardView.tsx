import { Sidebar } from './Sidebar';
import { Dashboard } from './Dashboard';
import { AIAssistant } from './AIAssistant';
import { TopMenuBar } from './TopMenuBar';

interface DashboardViewProps {
  currentView?: string;
  onViewChange?: (view: string) => void;
  onShowImportModal?: () => void;
}

export function DashboardView({ currentView, onViewChange, onShowImportModal }: DashboardViewProps) {
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
        <Sidebar activeView="dashboard" />
        
        {/* Zone centrale - Dashboard */}
        <Dashboard />
        
        {/* Panneau latéral droit - Assistant IA */}
        <AIAssistant />
      </div>
    </div>
  );
}
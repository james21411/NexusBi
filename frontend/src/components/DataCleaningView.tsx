import { DataGrid } from './DataGrid';
import { CleaningAssistant } from './CleaningAssistant';
import { TopMenuBar } from './TopMenuBar';
import { Sidebar } from './Sidebar';

interface DataCleaningViewProps {
  currentView?: string;
  onViewChange?: (view: string) => void;
  onShowImportModal?: () => void;
}

export function DataCleaningView({ currentView, onViewChange, onShowImportModal }: DataCleaningViewProps) {
  return (
    <div className="flex flex-col h-screen">
      {/* Menu supérieur type VSCode */}
      <TopMenuBar 
        currentView={currentView} 
        onViewChange={onViewChange}
        onShowImportModal={onShowImportModal}
      />
      
      <div className="flex flex-1 overflow-hidden bg-gray-50">
        {/* Barre latérale gauche */}
        <Sidebar activeView="data-sources" />
        
        {/* Zone principale - Data Grid */}
        <DataGrid />
        
        {/* Panneau latéral droit - Assistant IA de nettoyage */}
        <CleaningAssistant />
      </div>
    </div>
  );
}
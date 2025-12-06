import { useState } from 'react';
import { DashboardView } from './components/DashboardView';
import { DataCleaningView } from './components/DataCleaningView';
import { ReportsView } from './components/ReportsView';
import { DataSourcesView } from './components/DataSourcesView';
import { AnalyticsView } from './components/AnalyticsView';
import { SqlImportModal } from './components/SqlImportModal';

export default function App() {
  const [currentView, setCurrentView] = useState<'dashboard' | 'cleaning' | 'reports' | 'sources' | 'analytics'>('dashboard');
  const [showImportModal, setShowImportModal] = useState(false);

  const handleViewChange = (view: string) => {
    setCurrentView(view as 'dashboard' | 'cleaning' | 'reports' | 'sources' | 'analytics');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Vues */}
      {currentView === 'dashboard' && (
        <DashboardView 
          currentView={currentView}
          onViewChange={handleViewChange}
          onShowImportModal={() => setShowImportModal(true)}
        />
      )}
      {currentView === 'sources' && (
        <DataSourcesView 
          currentView={currentView}
          onViewChange={handleViewChange}
          onShowImportModal={() => setShowImportModal(true)}
        />
      )}
      {currentView === 'analytics' && (
        <AnalyticsView 
          currentView={currentView}
          onViewChange={handleViewChange}
          onShowImportModal={() => setShowImportModal(true)}
        />
      )}
      {currentView === 'reports' && (
        <ReportsView 
          currentView={currentView}
          onViewChange={handleViewChange}
          onShowImportModal={() => setShowImportModal(true)}
        />
      )}
      {currentView === 'cleaning' && (
        <DataCleaningView 
          currentView={currentView}
          onViewChange={handleViewChange}
          onShowImportModal={() => setShowImportModal(true)}
        />
      )}

      {/* Modale */}
      {showImportModal && <SqlImportModal onClose={() => setShowImportModal(false)} />}
    </div>
  );
}
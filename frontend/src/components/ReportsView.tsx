import { TopMenuBar } from './TopMenuBar';
import { Sidebar } from './Sidebar';
import { FileText, Calendar, Download, Share2, MoreVertical, Eye } from 'lucide-react';

interface ReportsViewProps {
  currentView?: string;
  onViewChange?: (view: string) => void;
  onShowImportModal?: () => void;
}

const reports = [
  { id: 1, name: 'Rapport Mensuel - Janvier 2025', type: 'PDF', date: '2025-01-31', status: 'Publié', views: 245 },
  { id: 2, name: 'Analyse Trimestrielle Q4 2024', type: 'Excel', date: '2024-12-31', status: 'Brouillon', views: 89 },
  { id: 3, name: 'Performance des Ventes', type: 'PDF', date: '2025-01-15', status: 'Publié', views: 412 },
  { id: 4, name: 'KPIs Opérationnels', type: 'PowerPoint', date: '2025-01-28', status: 'Publié', views: 178 },
  { id: 5, name: 'Analyse Client 2024', type: 'PDF', date: '2024-12-20', status: 'Archivé', views: 523 },
  { id: 6, name: 'Budget Prévisionnel 2025', type: 'Excel', date: '2025-01-05', status: 'Publié', views: 301 },
];

export function ReportsView({ currentView, onViewChange, onShowImportModal }: ReportsViewProps) {
  return (
    <div className="flex flex-col h-screen">
      <TopMenuBar 
        currentView={currentView} 
        onViewChange={onViewChange}
        onShowImportModal={onShowImportModal}
      />
      
      <div className="flex flex-1 overflow-hidden bg-gray-50">
        <Sidebar activeView="reports" />
        
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* En-tête */}
          <div className="bg-white border-b border-gray-200 px-8 py-6">
            <div className="flex items-center justify-between mb-2">
              <h1 className="text-gray-800">Rapports</h1>
              <button className="px-4 py-2 bg-[#0056D2] text-white rounded-lg hover:bg-[#0046b2] transition-colors">
                Nouveau rapport
              </button>
            </div>
            <p className="text-gray-600">Gérez et partagez vos rapports d'analyse</p>
          </div>

          {/* Filtres */}
          <div className="bg-white border-b border-gray-200 px-8 py-4 flex items-center gap-4">
            <select className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0056D2]">
              <option>Tous les types</option>
              <option>PDF</option>
              <option>Excel</option>
              <option>PowerPoint</option>
            </select>
            
            <select className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0056D2]">
              <option>Tous les statuts</option>
              <option>Publié</option>
              <option>Brouillon</option>
              <option>Archivé</option>
            </select>
            
            <div className="flex items-center gap-2 ml-auto">
              <Calendar size={18} className="text-gray-500" />
              <input
                type="date"
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0056D2]"
              />
            </div>
          </div>

          {/* Liste des rapports */}
          <div className="flex-1 overflow-auto p-8">
            <div className="grid grid-cols-1 gap-4">
              {reports.map((report) => (
                <div
                  key={report.id}
                  className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-4 flex-1">
                      <div className="w-12 h-12 bg-[#0056D2] rounded-lg flex items-center justify-center flex-shrink-0">
                        <FileText size={24} className="text-white" />
                      </div>
                      
                      <div className="flex-1">
                        <h3 className="text-gray-800 mb-1">{report.name}</h3>
                        <div className="flex items-center gap-4 text-gray-600">
                          <span>{report.type}</span>
                          <span>•</span>
                          <span>{report.date}</span>
                          <span>•</span>
                          <div className="flex items-center gap-1">
                            <Eye size={16} />
                            <span>{report.views} vues</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      <span className={`px-3 py-1 rounded-full text-white ${
                        report.status === 'Publié' ? 'bg-[#0056D2]' :
                        report.status === 'Brouillon' ? 'bg-[#FF6B00]' :
                        'bg-gray-400'
                      }`}>
                        {report.status}
                      </span>
                      
                      <button className="w-9 h-9 flex items-center justify-center text-gray-500 hover:bg-gray-100 rounded-lg transition-colors">
                        <Download size={18} />
                      </button>
                      
                      <button className="w-9 h-9 flex items-center justify-center text-gray-500 hover:bg-gray-100 rounded-lg transition-colors">
                        <Share2 size={18} />
                      </button>
                      
                      <button className="w-9 h-9 flex items-center justify-center text-gray-500 hover:bg-gray-100 rounded-lg transition-colors">
                        <MoreVertical size={18} />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
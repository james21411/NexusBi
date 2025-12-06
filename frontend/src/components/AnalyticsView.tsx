import { TopMenuBar } from './TopMenuBar';
import { Sidebar } from './Sidebar';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { TrendingUp, TrendingDown, Activity, DollarSign } from 'lucide-react';

interface AnalyticsViewProps {
  currentView?: string;
  onViewChange?: (view: string) => void;
  onShowImportModal?: () => void;
}

const salesData = [
  { month: 'Jan', ventes: 4000, previsions: 3800, couts: 2400 },
  { month: 'Fév', ventes: 3200, previsions: 3400, couts: 2210 },
  { month: 'Mar', ventes: 5000, previsions: 4500, couts: 2900 },
  { month: 'Avr', ventes: 4500, previsions: 4200, couts: 2700 },
  { month: 'Mai', ventes: 6000, previsions: 5500, couts: 3100 },
  { month: 'Jun', ventes: 5500, previsions: 5800, couts: 2950 },
  { month: 'Jul', ventes: 7200, previsions: 6800, couts: 3400 },
  { month: 'Aoû', ventes: 6800, previsions: 7000, couts: 3300 },
];

const revenueData = [
  { month: 'Jan', revenus: 12000 },
  { month: 'Fév', revenus: 15000 },
  { month: 'Mar', revenus: 18000 },
  { month: 'Avr', revenus: 16500 },
  { month: 'Mai', revenus: 21000 },
  { month: 'Jun', revenus: 19500 },
  { month: 'Jul', revenus: 24000 },
  { month: 'Aoû', revenus: 22500 },
];

export function AnalyticsView({ currentView, onViewChange, onShowImportModal }: AnalyticsViewProps) {
  return (
    <div className="flex flex-col h-screen">
      <TopMenuBar 
        currentView={currentView} 
        onViewChange={onViewChange}
        onShowImportModal={onShowImportModal}
      />
      
      <div className="flex flex-1 overflow-hidden bg-gray-50">
        <Sidebar activeView="analytics" />
        
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* En-tête */}
          <div className="bg-white border-b border-gray-200 px-8 py-6">
            <div className="flex items-center justify-between mb-2">
              <h1 className="text-gray-800">Analyses Avancées</h1>
              <div className="flex gap-3">
                <select className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0056D2]">
                  <option>Derniers 30 jours</option>
                  <option>Derniers 90 jours</option>
                  <option>Cette année</option>
                  <option>Année dernière</option>
                </select>
                <button className="px-4 py-2 bg-[#0056D2] text-white rounded-lg hover:bg-[#0046b2] transition-colors">
                  Exporter l'analyse
                </button>
              </div>
            </div>
            <p className="text-gray-600">Analyses détaillées de vos performances</p>
          </div>

          {/* Métriques principales */}
          <div className="bg-white border-b border-gray-200 px-8 py-6">
            <div className="grid grid-cols-4 gap-6">
              <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-5 border border-blue-200">
                <div className="flex items-center justify-between mb-3">
                  <div className="w-10 h-10 bg-[#0056D2] rounded-lg flex items-center justify-center">
                    <DollarSign size={20} className="text-white" />
                  </div>
                  <div className="flex items-center gap-1 text-green-600">
                    <TrendingUp size={16} />
                    <span>+12.5%</span>
                  </div>
                </div>
                <p className="text-gray-600 mb-1">Revenus Totaux</p>
                <p className="text-gray-800">148 500 €</p>
              </div>

              <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg p-5 border border-orange-200">
                <div className="flex items-center justify-between mb-3">
                  <div className="w-10 h-10 bg-[#FF6B00] rounded-lg flex items-center justify-center">
                    <Activity size={20} className="text-white" />
                  </div>
                  <div className="flex items-center gap-1 text-green-600">
                    <TrendingUp size={16} />
                    <span>+8.3%</span>
                  </div>
                </div>
                <p className="text-gray-600 mb-1">Taux de Conversion</p>
                <p className="text-gray-800">68.5%</p>
              </div>

              <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-5 border border-purple-200">
                <div className="flex items-center justify-between mb-3">
                  <div className="w-10 h-10 bg-purple-500 rounded-lg flex items-center justify-center">
                    <TrendingUp size={20} className="text-white" />
                  </div>
                  <div className="flex items-center gap-1 text-green-600">
                    <TrendingUp size={16} />
                    <span>+15.7%</span>
                  </div>
                </div>
                <p className="text-gray-600 mb-1">Croissance</p>
                <p className="text-gray-800">+23.4%</p>
              </div>

              <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-lg p-5 border border-red-200">
                <div className="flex items-center justify-between mb-3">
                  <div className="w-10 h-10 bg-red-500 rounded-lg flex items-center justify-center">
                    <TrendingDown size={20} className="text-white" />
                  </div>
                  <div className="flex items-center gap-1 text-red-600">
                    <TrendingDown size={16} />
                    <span>-3.2%</span>
                  </div>
                </div>
                <p className="text-gray-600 mb-1">Taux d'Abandon</p>
                <p className="text-gray-800">12.8%</p>
              </div>
            </div>
          </div>

          {/* Graphiques */}
          <div className="flex-1 overflow-auto p-8">
            <div className="grid grid-cols-1 gap-6 mb-6">
              {/* Graphique de ventes */}
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h3 className="text-gray-800 mb-1">Analyse des Ventes vs Prévisions</h3>
                    <p className="text-gray-600">Comparaison avec les objectifs</p>
                  </div>
                  <div className="flex gap-2">
                    <button className="px-3 py-1.5 bg-[#0056D2] text-white rounded text-sm">Mensuel</button>
                    <button className="px-3 py-1.5 border border-gray-300 text-gray-700 rounded text-sm hover:bg-gray-50">Trimestriel</button>
                    <button className="px-3 py-1.5 border border-gray-300 text-gray-700 rounded text-sm hover:bg-gray-50">Annuel</button>
                  </div>
                </div>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={salesData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis dataKey="month" stroke="#6b7280" />
                    <YAxis stroke="#6b7280" />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="ventes" stroke="#0056D2" strokeWidth={3} name="Ventes réelles" />
                    <Line type="monotone" dataKey="previsions" stroke="#FF6B00" strokeWidth={2} strokeDasharray="5 5" name="Prévisions" />
                    <Line type="monotone" dataKey="couts" stroke="#9ca3af" strokeWidth={2} name="Coûts" />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              {/* Graphique de revenus */}
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <div className="mb-6">
                  <h3 className="text-gray-800 mb-1">Évolution des Revenus</h3>
                  <p className="text-gray-600">Tendance sur 8 mois</p>
                </div>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={revenueData}>
                    <defs>
                      <linearGradient id="colorRevenus" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#0056D2" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#0056D2" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis dataKey="month" stroke="#6b7280" />
                    <YAxis stroke="#6b7280" />
                    <Tooltip />
                    <Area type="monotone" dataKey="revenus" stroke="#0056D2" strokeWidth={3} fillOpacity={1} fill="url(#colorRevenus)" name="Revenus (€)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Insights IA */}
            <div className="bg-gradient-to-r from-orange-50 to-orange-100 rounded-lg border border-orange-200 p-6">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-[#FF6B00] rounded-lg flex items-center justify-center flex-shrink-0">
                  <Activity size={24} className="text-white" />
                </div>
                <div>
                  <h3 className="text-gray-800 mb-2">Insights IA</h3>
                  <ul className="space-y-2 text-gray-700">
                    <li>• Les ventes de juillet dépassent les prévisions de 5.9%, une excellente performance</li>
                    <li>• Tendance à la hausse constante depuis mars (+44% sur 5 mois)</li>
                    <li>• Recommandation : Augmenter les stocks pour le mois prochain</li>
                    <li>• Attention : Le taux d'abandon a légèrement augmenté ce mois-ci</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
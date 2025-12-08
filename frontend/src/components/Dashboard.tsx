import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, AreaChart, Area, Legend } from 'recharts';
import { useState } from 'react';

const barData = [
  { name: 'Jan', value: 4000 },
  { name: 'Fév', value: 3000 },
  { name: 'Mar', value: 5000 },
  { name: 'Avr', value: 4500 },
  { name: 'Mai', value: 6000 },
  { name: 'Jun', value: 5500 },
];

// Données pour le graphique en barres groupées
const groupedBarData = [
  { month: 'Jan', variable1: 1500, variable2: 3000, variable3: 4500 },
  { month: 'Fév', variable1: 2000, variable2: 3500, variable3: 4000 },
  { month: 'Mar', variable1: 1800, variable2: 3200, variable3: 4800 },
  { month: 'Avr', variable1: 2200, variable2: 3800, variable3: 4200 },
  { month: 'Mai', variable1: 2500, variable2: 4000, variable3: 4500 },
  { month: 'Jun', variable1: 2800, variable2: 4200, variable3: 4800 },
];

// Données pour le graphique de fonction
const functionData = [
  { x: 0, y: 10 },
  { x: 1, y: 25 },
  { x: 2, y: 15 },
  { x: 3, y: 35 },
  { x: 4, y: 20 },
  { x: 5, y: 40 },
  { x: 6, y: 18 },
];

const pieData = [
  { name: 'Ventes', value: 400 },
  { name: 'Marketing', value: 300 },
  { name: 'Support', value: 200 },
  { name: 'R&D', value: 100 },
];

const COLORS = ['#FF6B00', '#0056D2', '#FFB800', '#00C49F'];

const tableData = [
  { id: 1, client: 'Entreprise A', montant: '125 000 €', statut: 'Confirmé', date: '2025-01-15' },
  { id: 2, client: 'Entreprise B', montant: '89 500 €', statut: 'En attente', date: '2025-01-18' },
  { id: 3, client: 'Entreprise C', montant: '210 000 €', statut: 'Confirmé', date: '2025-01-22' },
  { id: 4, client: 'Entreprise D', montant: '45 000 €', statut: 'Annulé', date: '2025-01-25' },
  { id: 5, client: 'Entreprise E', montant: '178 900 €', statut: 'Confirmé', date: '2025-02-01' },
];

export function Dashboard() {
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedChart, setSelectedChart] = useState<string | null>(null);
  const [selectedChartData, setSelectedChartData] = useState<any[] | null>(null);
  const [selectedChartTitle, setSelectedChartTitle] = useState('');

  const openModal = (chartType: string, data: any[], title: string) => {
    console.log('Opening modal for:', chartType, title);
    setSelectedChart(chartType);
    setSelectedChartData(data);
    setSelectedChartTitle(title);
    setModalOpen(true);
  };

  const closeModal = () => {
    setModalOpen(false);
  };

  const renderChartModal = () => {
    console.log('renderChartModal called, modalOpen:', modalOpen, 'selectedChart:', selectedChart);
    if (!modalOpen) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-[100] p-4" onClick={closeModal}>
        <div className="bg-[#3e3e42] rounded border border-[#454545] p-6 max-w-4xl w-full max-h-[90vh] overflow-auto relative" onClick={(e) => e.stopPropagation()}>
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-gray-200 text-lg font-medium">{selectedChartTitle}</h3>
            <button
              onClick={closeModal}
              className="text-gray-400 hover:text-gray-200 text-xl font-bold hover:bg-[#454545] rounded-full w-8 h-8 flex items-center justify-center"
            >
              ×
            </button>
          </div>
          <div className="h-[600px]">
            {selectedChart === 'bar' && selectedChartData && (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={selectedChartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#555555" />
                  <XAxis dataKey="name" stroke="#cccccc" fontSize={14} />
                  <YAxis stroke="#cccccc" fontSize={14} />
                  <Tooltip />
                  <Legend wrapperStyle={{ color: '#cccccc', fontSize: '14px' }} />
                  <Bar dataKey="value" fill="#007acc" radius={[4, 4, 0, 0]} name="Valeurs" />
                </BarChart>
              </ResponsiveContainer>
            )}

            {selectedChart === 'pie' && selectedChartData && (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={selectedChartData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }: { name: string, percent: number }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={120}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {selectedChartData.map((entry: any, index: number) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend wrapperStyle={{ color: '#cccccc', fontSize: '14px' }} />
                </PieChart>
              </ResponsiveContainer>
            )}

            {selectedChart === 'groupedBar' && selectedChartData && (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={selectedChartData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#555555" />
                  <XAxis type="number" stroke="#cccccc" fontSize={14} />
                  <YAxis dataKey="month" type="category" stroke="#cccccc" fontSize={14} />
                  <Tooltip />
                  <Legend wrapperStyle={{ color: '#cccccc', fontSize: '14px' }} />
                  <Bar dataKey="variable1" fill="#FF6B00" radius={[0, 0, 4, 4]} name="Variable 1" />
                  <Bar dataKey="variable2" fill="#007acc" radius={[0, 0, 4, 4]} name="Variable 2" />
                  <Bar dataKey="variable3" fill="#00C49F" radius={[0, 0, 4, 4]} name="Variable 3" />
                </BarChart>
              </ResponsiveContainer>
            )}

            {selectedChart === 'area' && selectedChartData && (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={selectedChartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#555555" />
                  <XAxis dataKey="x" stroke="#cccccc" fontSize={14} />
                  <YAxis stroke="#cccccc" fontSize={14} />
                  <Tooltip />
                  <Legend wrapperStyle={{ color: '#cccccc', fontSize: '14px' }} />
                  <Area type="monotone" dataKey="y" stroke="#00C49F" fill="#00C49F" fillOpacity={0.3} name="Zone" />
                  <Line type="monotone" dataKey="y" stroke="#007acc" strokeWidth={3} name="Ligne" />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </div>
    );
  };

  return (
    <main className="flex-1 bg-[#2d2d30] p-4 overflow-auto">
      {/* En-tête */}
      <header className="mb-4">
        <h1 className="text-gray-200 mb-1 text-lg">Tableau de Bord</h1>
        <p className="text-gray-400 text-sm">Vue d'ensemble de vos données</p>
      </header>

      {/* Statistiques KPI */}
      <section className="grid grid-cols-3 gap-4 mb-6">
        <article className="bg-[#3e3e42] p-4 rounded border border-[#454545]">
          <p className="text-gray-300 mb-1 text-sm">Revenus Totaux</p>
          <p className="text-[#007acc] font-medium">648 400 €</p>
        </article>
        <article className="bg-[#3e3e42] p-4 rounded border border-[#454545]">
          <p className="text-gray-300 mb-1 text-sm">Clients Actifs</p>
          <p className="text-[#007acc] font-medium">127</p>
        </article>
        <article className="bg-[#3e3e42] p-4 rounded border border-[#454545]">
          <p className="text-gray-300 mb-1 text-sm">Taux de Conversion</p>
          <p className="text-[#007acc] font-medium">68.5%</p>
        </article>
      </section>

      {/* Graphiques */}
      <section className="grid grid-cols-2 gap-4 mb-6">
        {/* Graphique en barres */}
        <article className="bg-[#3e3e42] p-4 rounded border border-[#454545] cursor-pointer" onClick={() => openModal('bar', barData, 'Évolution Mensuelle')}>
          <h3 className="text-gray-200 mb-3 text-sm font-medium">Évolution Mensuelle</h3>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={barData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#555555" />
              <XAxis dataKey="name" stroke="#cccccc" fontSize={12} />
              <YAxis stroke="#cccccc" fontSize={12} />
              <Tooltip />
              <Legend wrapperStyle={{ color: '#cccccc', fontSize: '12px' }} />
              <Bar dataKey="value" fill="#007acc" radius={[2, 2, 0, 0]} name="Valeurs" />
            </BarChart>
          </ResponsiveContainer>
        </article>

        {/* Diagramme circulaire */}
        <article className="bg-[#3e3e42] p-4 rounded border border-[#454545] cursor-pointer" onClick={() => openModal('pie', pieData, 'Répartition par Département')}>
          <h3 className="text-gray-200 mb-3 text-sm font-medium">Répartition par Département</h3>
          <ResponsiveContainer width="100%" height={180}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={60}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend wrapperStyle={{ color: '#cccccc', fontSize: '12px' }} />
            </PieChart>
          </ResponsiveContainer>
        </article>
      </section>

      {/* Deuxième ligne de graphiques - 2 nouveaux graphiques */}
      <section className="grid grid-cols-2 gap-4 mb-6">
        {/* Graphique en barres groupées pivoté */}
        <article className="bg-[#3e3e42] p-4 rounded border border-[#454545] cursor-pointer" onClick={() => openModal('groupedBar', groupedBarData, 'Performance par Variable')}>
          <h3 className="text-gray-200 mb-3 text-sm font-medium">Performance par Variable</h3>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={groupedBarData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#555555" />
              <XAxis type="number" stroke="#cccccc" fontSize={12} />
              <YAxis dataKey="month" type="category" stroke="#cccccc" fontSize={12} />
              <Tooltip />
              <Legend wrapperStyle={{ color: '#cccccc', fontSize: '12px' }} />
              <Bar dataKey="variable1" fill="#FF6B00" radius={[0, 0, 2, 2]} name="Variable 1" />
              <Bar dataKey="variable2" fill="#007acc" radius={[0, 0, 2, 2]} name="Variable 2" />
              <Bar dataKey="variable3" fill="#00C49F" radius={[0, 0, 2, 2]} name="Variable 3" />
            </BarChart>
          </ResponsiveContainer>
        </article>

        {/* Graphique de fonction */}
        <article className="bg-[#3e3e42] p-4 rounded border border-[#454545] cursor-pointer" onClick={() => openModal('area', functionData, 'Analyse Fonctionnelle')}>
          <h3 className="text-gray-200 mb-3 text-sm font-medium">Analyse Fonctionnelle</h3>
          <ResponsiveContainer width="100%" height={180}>
            <AreaChart data={functionData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#555555" />
              <XAxis dataKey="x" stroke="#cccccc" fontSize={12} />
              <YAxis stroke="#cccccc" fontSize={12} />
              <Tooltip />
              <Legend wrapperStyle={{ color: '#cccccc', fontSize: '12px' }} />
              <Area type="monotone" dataKey="y" stroke="#00C49F" fill="#00C49F" fillOpacity={0.3} name="Zone" />
              <Line type="monotone" dataKey="y" stroke="#007acc" strokeWidth={2} name="Ligne" />
            </AreaChart>
          </ResponsiveContainer>
        </article>
      </section>

      {/* Tableau de données */}
      <section className="bg-[#3e3e42] rounded border border-[#454545] overflow-hidden">
        <header className="bg-[#454545] px-4 py-2 border-b border-[#555555]">
          <h3 className="text-gray-200 text-sm font-medium">Transactions Récentes</h3>
        </header>
        <table className="w-full">
          <thead className="bg-[#454545] border-b border-[#555555]">
            <tr>
              <th className="px-4 py-2 text-left text-gray-300 text-sm">ID</th>
              <th className="px-4 py-2 text-left text-gray-300 text-sm">Client</th>
              <th className="px-4 py-2 text-left text-gray-300 text-sm">Montant</th>
              <th className="px-4 py-2 text-left text-gray-300 text-sm">Statut</th>
              <th className="px-4 py-2 text-left text-gray-300 text-sm">Date</th>
            </tr>
          </thead>
          <tbody>
            {tableData.map((row) => (
              <tr key={row.id} className="border-b border-[#555555] hover:bg-[#454545]">
                <td className="px-4 py-2 text-gray-200 text-sm">{row.id}</td>
                <td className="px-4 py-2 text-gray-200 text-sm">{row.client}</td>
                <td className="px-4 py-2 text-gray-200 text-sm">{row.montant}</td>
                <td className="px-4 py-2">
                  <span className={`px-2 py-0.5 rounded text-xs text-white ${
                    row.statut === 'Confirmé' ? 'bg-[#007acc]' :
                    row.statut === 'En attente' ? 'bg-[#FF6B00]' :
                    'bg-gray-400'
                  }`}>
                    {row.statut}
                  </span>
                </td>
                <td className="px-4 py-2 text-gray-200 text-sm">{row.date}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
      {renderChartModal()}
    </main>
  );
}

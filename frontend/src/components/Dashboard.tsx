import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const barData = [
  { name: 'Jan', value: 4000 },
  { name: 'Fév', value: 3000 },
  { name: 'Mar', value: 5000 },
  { name: 'Avr', value: 4500 },
  { name: 'Mai', value: 6000 },
  { name: 'Jun', value: 5500 },
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
  return (
    <div className="flex-1 bg-white p-8 overflow-auto">
      {/* En-tête */}
      <div className="mb-8">
        <h1 className="text-gray-800 mb-2">Tableau de Bord</h1>
        <p className="text-gray-500">Vue d'ensemble de vos données</p>
      </div>

      {/* Statistiques KPI */}
      <div className="grid grid-cols-3 gap-6 mb-8">
        <div className="bg-gray-50 p-6 rounded-lg border border-gray-200">
          <p className="text-gray-600 mb-2">Revenus Totaux</p>
          <p className="text-[#0056D2]">648 400 €</p>
        </div>
        <div className="bg-gray-50 p-6 rounded-lg border border-gray-200">
          <p className="text-gray-600 mb-2">Clients Actifs</p>
          <p className="text-[#0056D2]">127</p>
        </div>
        <div className="bg-gray-50 p-6 rounded-lg border border-gray-200">
          <p className="text-gray-600 mb-2">Taux de Conversion</p>
          <p className="text-[#FF6B00]">68.5%</p>
        </div>
      </div>

      {/* Graphiques */}
      <div className="grid grid-cols-2 gap-6 mb-8">
        {/* Graphique en barres */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h3 className="text-gray-700 mb-4">Évolution Mensuelle</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={barData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="name" stroke="#6b7280" />
              <YAxis stroke="#6b7280" />
              <Tooltip />
              <Bar dataKey="value" fill="#0056D2" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Diagramme circulaire */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h3 className="text-gray-700 mb-4">Répartition par Département</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Tableau de données */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
          <h3 className="text-gray-700">Transactions Récentes</h3>
        </div>
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-6 py-3 text-left text-gray-600">ID</th>
              <th className="px-6 py-3 text-left text-gray-600">Client</th>
              <th className="px-6 py-3 text-left text-gray-600">Montant</th>
              <th className="px-6 py-3 text-left text-gray-600">Statut</th>
              <th className="px-6 py-3 text-left text-gray-600">Date</th>
            </tr>
          </thead>
          <tbody>
            {tableData.map((row) => (
              <tr key={row.id} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="px-6 py-4 text-gray-700">{row.id}</td>
                <td className="px-6 py-4 text-gray-700">{row.client}</td>
                <td className="px-6 py-4 text-gray-700">{row.montant}</td>
                <td className="px-6 py-4">
                  <span className={`px-3 py-1 rounded-full text-white ${
                    row.statut === 'Confirmé' ? 'bg-[#0056D2]' :
                    row.statut === 'En attente' ? 'bg-[#FF6B00]' :
                    'bg-gray-400'
                  }`}>
                    {row.statut}
                  </span>
                </td>
                <td className="px-6 py-4 text-gray-700">{row.date}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

import { Search, Filter, Download } from 'lucide-react';

// Données de démonstration avec quelques erreurs
const gridData = [
  { id: 1, nom: 'Dupont', prenom: 'Jean', email: 'jean.dupont@email.com', telephone: '0123456789', ville: 'Paris', statut: 'Actif', montant: '1250' },
  { id: 2, nom: 'Martin', prenom: 'Marie', email: 'marie.martin@email.com', telephone: '0234567890', ville: 'Lyon', statut: 'Actif', montant: '3400' },
  { id: 3, nom: 'Bernard', prenom: '', email: 'bernard@email.com', telephone: '', ville: 'Marseille', statut: 'Inactif', montant: '890', error: true },
  { id: 4, nom: 'Petit', prenom: 'Pierre', email: 'pierre.petit@email.com', telephone: '0456789012', ville: 'Toulouse', statut: 'Actif', montant: '2100' },
  { id: 5, nom: 'Dubois', prenom: 'Sophie', email: '', telephone: '0567890123', ville: '', statut: 'Actif', montant: '1780', error: true },
  { id: 6, nom: 'Thomas', prenom: 'Luc', email: 'luc.thomas@email.com', telephone: '0678901234', ville: 'Nice', statut: 'Actif', montant: '4200' },
  { id: 7, nom: 'Robert', prenom: 'Claire', email: 'claire.robert@email.com', telephone: '', ville: 'Nantes', statut: 'Inactif', montant: '', error: true },
  { id: 8, nom: 'Richard', prenom: 'Paul', email: 'paul.richard@email.com', telephone: '0890123456', ville: 'Strasbourg', statut: 'Actif', montant: '1950' },
  { id: 9, nom: 'Durand', prenom: '', email: 'durand@email.com', telephone: '0901234567', ville: 'Montpellier', statut: 'Actif', montant: '3100', error: true },
  { id: 10, nom: 'Moreau', prenom: 'Julie', email: 'julie.moreau@email.com', telephone: '0012345678', ville: 'Bordeaux', statut: 'Actif', montant: '2600' },
  { id: 11, nom: 'Simon', prenom: 'Marc', email: '', telephone: '0123450987', ville: 'Lille', statut: 'Inactif', montant: '1400', error: true },
  { id: 12, nom: 'Laurent', prenom: 'Emma', email: 'emma.laurent@email.com', telephone: '0234561098', ville: 'Rennes', statut: 'Actif', montant: '2850' },
  { id: 13, nom: 'Lefebvre', prenom: 'Thomas', email: 'thomas.lefebvre@email.com', telephone: '0345612109', ville: 'Reims', statut: 'Actif', montant: '3700' },
  { id: 14, nom: 'Michel', prenom: 'Alice', email: 'alice.michel@email.com', telephone: '', ville: 'Le Havre', statut: 'Actif', montant: '', error: true },
  { id: 15, nom: 'Garcia', prenom: 'Lucas', email: 'lucas.garcia@email.com', telephone: '0567823210', ville: 'Saint-Étienne', statut: 'Actif', montant: '1620' },
];

export function DataGrid() {
  return (
    <div className="flex-1 flex flex-col bg-white">
      {/* Barre d'outils */}
      <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h1 className="text-gray-800">Nettoyage de Données</h1>
          <div className="flex items-center gap-2 ml-6">
            <div className="relative">
              <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Rechercher..."
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0056D2] focus:border-transparent w-64"
              />
            </div>
            <button className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors flex items-center gap-2">
              <Filter size={18} />
              Filtrer
            </button>
          </div>
        </div>
        <button className="px-4 py-2 bg-[#0056D2] text-white rounded-lg hover:bg-[#0046b2] transition-colors flex items-center gap-2">
          <Download size={18} />
          Exporter
        </button>
      </div>

      {/* Grille de données */}
      <div className="flex-1 overflow-auto">
        <table className="w-full">
          <thead className="bg-gray-50 sticky top-0 z-10">
            <tr className="border-b border-gray-200">
              <th className="px-6 py-3 text-left text-gray-600">
                <input type="checkbox" className="rounded" />
              </th>
              <th className="px-6 py-3 text-left text-gray-600">ID</th>
              <th className="px-6 py-3 text-left text-gray-600">Nom</th>
              <th className="px-6 py-3 text-left text-gray-600">Prénom</th>
              <th className="px-6 py-3 text-left text-gray-600">Email</th>
              <th className="px-6 py-3 text-left text-gray-600">Téléphone</th>
              <th className="px-6 py-3 text-left text-gray-600">Ville</th>
              <th className="px-6 py-3 text-left text-gray-600">Statut</th>
              <th className="px-6 py-3 text-left text-gray-600">Montant</th>
            </tr>
          </thead>
          <tbody>
            {gridData.map((row) => (
              <tr 
                key={row.id} 
                className="border-b border-gray-100 hover:bg-gray-50 transition-colors"
              >
                <td className="px-6 py-4">
                  <input type="checkbox" className="rounded" />
                </td>
                <td className="px-6 py-4 text-gray-700">{row.id}</td>
                <td className="px-6 py-4 text-gray-700">{row.nom}</td>
                <td className={`px-6 py-4 ${!row.prenom && row.error ? 'bg-orange-100' : 'text-gray-700'}`}>
                  {row.prenom || '—'}
                </td>
                <td className={`px-6 py-4 ${!row.email && row.error ? 'bg-orange-100' : 'text-gray-700'}`}>
                  {row.email || '—'}
                </td>
                <td className={`px-6 py-4 ${!row.telephone && row.error ? 'bg-orange-100' : 'text-gray-700'}`}>
                  {row.telephone || '—'}
                </td>
                <td className={`px-6 py-4 ${!row.ville && row.error ? 'bg-orange-100' : 'text-gray-700'}`}>
                  {row.ville || '—'}
                </td>
                <td className="px-6 py-4">
                  <span className={`px-3 py-1 rounded-full text-white ${
                    row.statut === 'Actif' ? 'bg-[#0056D2]' : 'bg-gray-400'
                  }`}>
                    {row.statut}
                  </span>
                </td>
                <td className={`px-6 py-4 ${!row.montant && row.error ? 'bg-orange-100' : 'text-gray-700'}`}>
                  {row.montant ? `${row.montant} €` : '—'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pied de page avec pagination */}
      <div className="bg-white border-t border-gray-200 px-6 py-4 flex items-center justify-between">
        <p className="text-gray-600">15 lignes • 6 erreurs détectées</p>
        <div className="flex items-center gap-2">
          <button className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors">
            Précédent
          </button>
          <button className="px-4 py-2 bg-[#0056D2] text-white rounded-lg">1</button>
          <button className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors">2</button>
          <button className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors">3</button>
          <button className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors">
            Suivant
          </button>
        </div>
      </div>
    </div>
  );
}

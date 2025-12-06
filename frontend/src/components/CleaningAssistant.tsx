import { Sparkles, AlertTriangle, CheckCircle2 } from 'lucide-react';

export function CleaningAssistant() {
  return (
    <div className="w-96 bg-gray-50 border-l border-gray-200 flex flex-col">
      {/* En-tête */}
      <div className="bg-white px-6 py-5 border-b border-gray-200 flex items-center gap-3">
        <div className="w-8 h-8 bg-[#FF6B00] rounded-lg flex items-center justify-center">
          <Sparkles size={18} className="text-white" />
        </div>
        <h2 className="text-gray-800">Nexus Assistant</h2>
      </div>

      {/* Zone de conversation */}
      <div className="flex-1 overflow-auto p-6 space-y-4">
        {/* Message IA - Bienvenue */}
        <div className="flex justify-start">
          <div className="max-w-[85%] px-4 py-3 rounded-lg bg-white border border-[#FF6B00] text-gray-800 rounded-bl-none">
            Analyse en cours de vos données...
          </div>
        </div>

        {/* Message IA - Détection d'erreurs */}
        <div className="flex justify-start">
          <div className="max-w-[85%] rounded-lg bg-white border border-[#FF6B00] overflow-hidden rounded-bl-none">
            <div className="px-4 py-3 text-gray-800">
              <div className="flex items-start gap-2 mb-3">
                <AlertTriangle size={20} className="text-[#FF6B00] flex-shrink-0 mt-0.5" />
                <div>
                  <p className="mb-2">J'ai détecté <span className="text-[#FF6B00]">6 erreurs</span> dans vos données :</p>
                </div>
              </div>
              <ul className="space-y-2 ml-7 text-gray-700">
                <li>• 3 valeurs manquantes dans la colonne "Prénom"</li>
                <li>• 2 emails manquants</li>
                <li>• 4 numéros de téléphone vides</li>
                <li>• 1 ville non renseignée</li>
                <li>• 2 montants invalides</li>
              </ul>
            </div>
            <div className="bg-orange-50 px-4 py-3 border-t border-orange-100">
              <p className="text-gray-700 mb-3">Voulez-vous les corriger automatiquement ?</p>
              <div className="flex gap-2">
                <button className="flex-1 px-4 py-2 bg-[#0056D2] text-white rounded-lg hover:bg-[#0046b2] transition-colors flex items-center justify-center gap-2">
                  <CheckCircle2 size={16} />
                  Valider la correction
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Message utilisateur */}
        <div className="flex justify-end">
          <div className="max-w-[85%] px-4 py-3 rounded-lg bg-[#0056D2] text-white rounded-br-none">
            Quelles sont les options de correction disponibles ?
          </div>
        </div>

        {/* Message IA - Options */}
        <div className="flex justify-start">
          <div className="max-w-[85%] px-4 py-3 rounded-lg bg-white border border-[#FF6B00] text-gray-800 rounded-bl-none">
            <p className="mb-3">Voici les options de correction :</p>
            <div className="space-y-2">
              <div className="bg-gray-50 px-3 py-2 rounded border border-gray-200">
                <p className="text-gray-800 mb-1">1. Suppression des lignes</p>
                <p className="text-gray-600">Supprimer les 6 lignes avec erreurs</p>
              </div>
              <div className="bg-blue-50 px-3 py-2 rounded border border-[#0056D2]">
                <p className="text-gray-800 mb-1">2. Complétion intelligente</p>
                <p className="text-gray-600">Remplir avec des valeurs similaires (Recommandé)</p>
              </div>
              <div className="bg-gray-50 px-3 py-2 rounded border border-gray-200">
                <p className="text-gray-800 mb-1">3. Valeur par défaut</p>
                <p className="text-gray-600">Remplir avec "N/A" ou "Non renseigné"</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Statistiques */}
      <div className="bg-white px-6 py-4 border-t border-gray-200">
        <div className="grid grid-cols-2 gap-3 mb-4">
          <div className="bg-red-50 px-3 py-2 rounded border border-red-200">
            <p className="text-gray-600">Erreurs</p>
            <p className="text-red-600">6</p>
          </div>
          <div className="bg-green-50 px-3 py-2 rounded border border-green-200">
            <p className="text-gray-600">Valides</p>
            <p className="text-green-600">9</p>
          </div>
        </div>
        
        <button className="w-full px-4 py-2 bg-[#FF6B00] text-white rounded-lg hover:bg-[#e56100] transition-colors">
          Lancer le nettoyage
        </button>
      </div>
    </div>
  );
}

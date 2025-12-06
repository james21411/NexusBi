import { X, FileText, Upload } from 'lucide-react';
import { useState } from 'react';

interface SqlImportModalProps {
  onClose: () => void;
}

export function SqlImportModal({ onClose }: SqlImportModalProps) {
  const [activeTab, setActiveTab] = useState('sql');
  const [isDragging, setIsDragging] = useState(false);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Overlay avec flou */}
      <div 
        className="absolute inset-0 bg-black/30 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* Modale */}
      <div className="relative bg-white rounded-xl shadow-2xl w-[600px] max-w-[90vw]">
        {/* En-tête */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-gray-200">
          <h2 className="text-gray-800">Importer une nouvelle source</h2>
          <button 
            onClick={onClose}
            className="w-8 h-8 flex items-center justify-center text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        {/* Onglets */}
        <div className="flex border-b border-gray-200 px-6">
          <button
            onClick={() => setActiveTab('database')}
            className={`px-6 py-3 relative transition-colors ${
              activeTab === 'database'
                ? 'text-gray-800'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Base de données
            {activeTab === 'database' && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#FF6B00]" />
            )}
          </button>
          
          <button
            onClick={() => setActiveTab('sql')}
            className={`px-6 py-3 relative transition-colors ${
              activeTab === 'sql'
                ? 'text-gray-800'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Fichier Dump SQL
            {activeTab === 'sql' && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#FF6B00]" />
            )}
          </button>
          
          <button
            onClick={() => setActiveTab('api')}
            className={`px-6 py-3 relative transition-colors ${
              activeTab === 'api'
                ? 'text-gray-800'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            API REST
            {activeTab === 'api' && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#FF6B00]" />
            )}
          </button>
        </div>

        {/* Contenu principal */}
        <div className="p-8">
          {/* Zone de drag & drop */}
          <div
            className={`border-2 border-dashed rounded-lg p-12 flex flex-col items-center justify-center transition-all ${
              isDragging
                ? 'border-[#0056D2] bg-blue-50'
                : 'border-[#0056D2] bg-gray-50'
            }`}
            onDragOver={(e) => {
              e.preventDefault();
              setIsDragging(true);
            }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={(e) => {
              e.preventDefault();
              setIsDragging(false);
            }}
          >
            {/* Icône fichier SQL */}
            <div className="w-20 h-20 bg-[#0056D2] rounded-xl flex items-center justify-center mb-4">
              <FileText size={40} className="text-white" />
            </div>
            
            <p className="text-gray-700 mb-2">Glissez-déposez votre fichier .SQL ici</p>
            <p className="text-gray-500 mb-4">ou</p>
            
            <button className="px-6 py-2 bg-white border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors flex items-center gap-2">
              <Upload size={18} />
              Parcourir les fichiers
            </button>
          </div>

          {/* Note de sécurité */}
          <div className="mt-6 flex items-start gap-2 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="w-5 h-5 bg-[#0056D2] rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
              <span className="text-white">i</span>
            </div>
            <p className="text-gray-700">
              <span>Analyse sécurisée via conteneur temporaire</span>
            </p>
          </div>
        </div>

        {/* Pied de page avec boutons */}
        <div className="flex justify-end gap-3 px-6 py-5 bg-gray-50 border-t border-gray-200 rounded-b-xl">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-white border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
          >
            Annuler
          </button>
          <button className="px-6 py-2 bg-[#FF6B00] text-white rounded-lg hover:bg-[#e56100] transition-colors">
            Analyser
          </button>
        </div>
      </div>
    </div>
  );
}

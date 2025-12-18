 import { X, FileText, Upload, Database, Table, FileSpreadsheet, FileJson, File } from 'lucide-react';
import { useState } from 'react';
import { createDataSource } from '../api/service';
import { API_BASE_URL } from '../api/config';
import { useAuth } from '../api/authContext';

interface SqlImportModalProps {
  onClose: () => void;
  onDataSourceCreated?: () => void;
}

const fileTypes = [
  {
    id: 'csv',
    name: 'CSV',
    description: 'Fichiers de valeurs séparées par des virgules',
    icon: FileText,
    color: 'bg-green-500',
    extensions: ['.csv']
  },
  {
    id: 'excel',
    name: 'Excel',
    description: 'Fichiers Microsoft Excel',
    icon: FileSpreadsheet,
    color: 'bg-blue-500',
    extensions: ['.xlsx', '.xls']
  },
  {
    id: 'json',
    name: 'JSON',
    description: 'Fichiers JSON structurés',
    icon: FileJson,
    color: 'bg-orange-500',
    extensions: ['.json']
  },
  {
    id: 'txt',
    name: 'TXT',
    description: 'Fichiers texte formatés',
    icon: File,
    color: 'bg-gray-500',
    extensions: ['.txt']
  },
  {
    id: 'sql',
    name: 'SQL Dump',
    description: 'Sauvegardes de bases de données SQL',
    icon: Database,
    color: 'bg-purple-500',
    extensions: ['.sql']
  }
];

export function SqlImportModal({ onClose, onDataSourceCreated }: SqlImportModalProps) {
  const [activeTab, setActiveTab] = useState('files');
  const [selectedFileType, setSelectedFileType] = useState('csv');
  const [isDragging, setIsDragging] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [showConfigModal, setShowConfigModal] = useState(false);
  const [previewData, setPreviewData] = useState<any[]>([]);
  const [showPreview, setShowPreview] = useState(false);
  const [detectedSettings, setDetectedSettings] = useState<{
    encoding: string;
    delimiter: string;
    columns: number;
    rows: number;
  } | null>(null);
  const { token: authToken } = useAuth();

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setUploadedFile(file);
      console.log('Fichier sélectionné:', file.name, 'Taille:', file.size, 'Type:', file.type);
    }
  };

  const handleDrop = (event: React.DragEvent) => {
    event.preventDefault();
    setIsDragging(false);
    
    const files = Array.from(event.dataTransfer.files);
    if (files.length > 0) {
      setUploadedFile(files[0]);
    }
  };

  const handleDragOver = (event: React.DragEvent) => {
    event.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleAnalyze = async () => {
    if (!uploadedFile) return;

    // Pour les fichiers CSV, d'abord détecter les paramètres automatiquement
    if (selectedFileType === 'csv') {
      try {
        // Créer FormData pour l'analyse
        const formData = new FormData();
        formData.append('file', uploadedFile);

        const response = await fetch(`${API_BASE_URL}/data-sources/analyze`, {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          console.error('Erreur lors de l\'analyse');
          return;
        }

        const result = await response.json();
        setDetectedSettings(result);
        setShowConfigModal(true); // Montrer les paramètres détectés

      } catch (error) {
        console.error('Erreur lors de l\'analyse:', error);
        // Fallback vers l'ancien comportement
        setShowConfigModal(true);
      }
    } else if (selectedFileType === 'txt') {
      setShowConfigModal(true);
    } else {
      // Pour les autres formats, charger directement
      handleLoadFile();
    }
  };

  const handleLoadFile = (config?: any) => {
    if (!uploadedFile) return;

    // Simuler le chargement et la conversion en DataFrame
    const mockData = [
      { Colonne1: 'Valeur1', Colonne2: 'Valeur2', Colonne3: '123' },
      { Colonne1: 'Valeur4', Colonne2: 'Valeur5', Colonne3: '456' },
      { Colonne1: 'Valeur7', Colonne2: 'Valeur8', Colonne3: '789' }
    ];

    setPreviewData(mockData);
    setShowPreview(true);
    
    // Fermer les modals
    setShowConfigModal(false);
    // Note: On ne ferme pas le modal principal pour permettre de voir la prévisualisation
  };

  const handleConfirmLoad = async () => {
    if (!uploadedFile) return;

    try {
      // Créer FormData pour l'upload du fichier
      const formData = new FormData();
      formData.append('file', uploadedFile);
      formData.append('name', uploadedFile.name.replace(/\.[^/.]+$/, "")); // Nom sans extension
      formData.append('project_id', '1'); // TODO: Utiliser le vrai ID du projet

      console.log('Upload du fichier:', uploadedFile.name, 'Type:', selectedFileType);

      // Upload du fichier vers le backend
      const response = await fetch(`${API_BASE_URL}/data-sources/upload`, {
        method: 'POST',
        body: formData,
        headers: authToken ? { Authorization: `Bearer ${authToken}` } : {},
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error('Erreur lors de l\'upload:', errorData);
        return;
      }

      const result = await response.json();
      console.log('Source de données créée:', result);

      // Notifier le parent pour recharger la liste
      if (onDataSourceCreated) {
        onDataSourceCreated();
      }

      onClose();
    } catch (error) {
      console.error('Erreur lors de l\'upload:', error);
    }
  };

  const selectedType = fileTypes.find(type => type.id === selectedFileType);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Overlay avec flou */}
      <div 
        className="absolute inset-0 bg-black/30 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* Modale */}
      <div className="relative bg-white rounded-xl shadow-2xl w-[700px] max-w-[95vw] h-[600px] max-h-[95vh] overflow-hidden flex flex-col">
        {/* En-tête */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 flex-shrink-0">
          <h2 className="text-gray-800 text-lg font-semibold">Importer une nouvelle source</h2>
          <button
            onClick={onClose}
            className="w-8 h-8 flex items-center justify-center text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        {/* Onglets */}
        <div className="flex border-b border-gray-200 px-6 flex-shrink-0">
          <button
            onClick={() => setActiveTab('files')}
            className={`px-5 py-3 relative transition-colors text-base font-medium ${
              activeTab === 'files'
                ? 'text-gray-800'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Fichiers
            {activeTab === 'files' && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#FF6B00]" />
            )}
          </button>
          
          <button
            onClick={() => setActiveTab('database')}
            className={`px-5 py-3 relative transition-colors text-base font-medium ${
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
            onClick={() => setActiveTab('api')}
            className={`px-5 py-3 relative transition-colors text-base font-medium ${
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
        <div className="flex-1 overflow-y-auto p-4">
          {activeTab === 'files' && (
            <div className="flex gap-4 h-full">
              {/* Section gauche - Types de fichiers - Largeur adaptative */}
              <div className="w-64 flex-shrink-0">
                <h3 className="text-base font-semibold text-gray-800 mb-4">Type de fichier</h3>
                <div className="space-y-3">
                  {fileTypes.map((type) => {
                    const Icon = type.icon;
                    return (
                      <button
                        key={type.id}
                        onClick={() => setSelectedFileType(type.id)}
                        className={`w-full p-4 border-2 rounded-lg text-left transition-all ${
                          selectedFileType === type.id
                            ? 'border-[#0056D2] bg-blue-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <div className="flex items-center gap-3">
                          <div className={`w-9 h-9 ${type.color} rounded-lg flex items-center justify-center flex-shrink-0`}>
                            <Icon size={18} className="text-white" />
                          </div>
                          <div className="min-w-0">
                            <h4 className="font-semibold text-gray-800 text-base">{type.name}</h4>
                            <p className="text-sm text-gray-600 truncate">{type.description}</p>
                            <p className="text-sm text-gray-500">
                              {type.extensions.join(', ')}
                            </p>
                          </div>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Section droite - Zone de drop et configuration */}
              <div className="flex-1 flex flex-col">
                <h3 className="text-base font-semibold text-gray-800 mb-4">Sélectionner un fichier</h3>
                
                {/* Zone de drag & drop */}
                <div
                  className={`flex-1 border-2 border-dashed rounded-lg p-6 flex flex-col items-center justify-center transition-all min-h-[320px] ${
                    isDragging
                      ? 'border-[#0056D2] bg-blue-50'
                      : 'border-gray-300 bg-gray-50'
                  }`}
                  onDrop={handleDrop}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                >
                  {selectedType && (
                    <>
                      <div className={`w-14 h-14 ${selectedType.color} rounded-xl flex items-center justify-center mb-4`}>
                        <selectedType.icon size={28} className="text-white" />
                      </div>
                      
                      {uploadedFile ? (
                        <div className="text-center">
                          <p className="text-gray-700 font-semibold mb-2 text-base">{uploadedFile.name}</p>
                          <p className="text-sm text-gray-500 mb-4">
                            {uploadedFile.size > 0 ? `${uploadedFile.size.toLocaleString()} octets (${(uploadedFile.size / 1024 / 1024).toFixed(2)} MB)` : 'Calcul en cours...'}
                          </p>
                          <button
                            onClick={() => setUploadedFile(null)}
                            className="text-sm text-[#0056D2] hover:underline"
                          >
                            Changer de fichier
                          </button>
                        </div>
                      ) : (
                        <>
                          <p className="text-gray-700 mb-2 text-center text-base font-medium">
                            Glissez-déposez votre fichier {selectedType.name} ici
                          </p>
                          <p className="text-gray-500 mb-4">ou</p>
                          
                          <label className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors flex items-center gap-2 cursor-pointer">
                            <Upload size={18} />
                            Parcourir les fichiers
                            <input
                              key={`file-input-${selectedFileType}`}
                              type="file"
                              accept={selectedType.extensions.join(',')}
                              onChange={handleFileSelect}
                              className="hidden"
                            />
                          </label>
                        </>
                      )}
                    </>
                  )}
                </div>

                {/* Note de sécurité */}
                <div className="mt-4 flex items-start gap-2 bg-blue-50 border border-blue-200 rounded-lg p-3">
                  <div className="w-5 h-5 bg-[#0056D2] rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-white text-xs">i</span>
                  </div>
                  <p className="text-gray-700 text-sm">
                    <span className="font-medium">Analyse sécurisée:</span> Vos fichiers sont traités de manière sécurisée.
                  </p>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'database' && (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <Database size={64} className="mx-auto text-gray-400 mb-4" />
                <h3 className="text-lg font-semibold text-gray-800 mb-2">Connexion base de données</h3>
                <p className="text-gray-600 text-base">Configuration des connexions aux bases de données</p>
                <p className="text-sm text-gray-500 mt-2">Fonctionnalité en développement</p>
              </div>
            </div>
          )}

          {activeTab === 'api' && (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <Table size={64} className="mx-auto text-gray-400 mb-4" />
                <h3 className="text-lg font-semibold text-gray-800 mb-2">API REST</h3>
                <p className="text-gray-600 text-base">Configuration des APIs REST externes</p>
                <p className="text-sm text-gray-500 mt-2">Fonctionnalité en développement</p>
              </div>
            </div>
          )}
        </div>

        {/* Pied de page avec boutons */}
        <div className="flex justify-end gap-3 px-6 py-4 bg-gray-50 border-t border-gray-200 flex-shrink-0">
          <button
            onClick={onClose}
            className="px-6 py-3 bg-white border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors text-base font-medium"
          >
            Annuler
          </button>
          <button
            onClick={handleAnalyze}
            disabled={!uploadedFile}
            className="px-6 py-3 bg-[#FF6B00] text-white rounded-lg hover:bg-[#e56100] transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-base font-medium"
          >
            Charger
          </button>
        </div>
      </div>

      {/* Modal de configuration pour CSV/TXT */}
      {showConfigModal && (
        <FileConfigModal
          fileType={selectedFileType}
          detectedSettings={detectedSettings}
          onClose={() => setShowConfigModal(false)}
          onConfirm={(config) => handleLoadFile(config)}
        />
      )}

      {/* Modal de prévisualisation des données */}
      {showPreview && (
        <DataPreviewModal
          data={previewData}
          fileName={uploadedFile?.name || ''}
          onClose={() => setShowPreview(false)}
          onConfirm={handleConfirmLoad}
        />
      )}
    </div>
  );
}

// Modal de configuration des fichiers
interface FileConfigModalProps {
  fileType: string;
  detectedSettings?: {
    encoding: string;
    delimiter: string;
    columns: number;
    rows: number;
  } | null;
  onClose: () => void;
  onConfirm: (config: any) => void;
}

function FileConfigModal({ fileType, detectedSettings, onClose, onConfirm }: FileConfigModalProps) {
  const [delimiter, setDelimiter] = useState(detectedSettings?.delimiter || ',');
  const [decimalSeparator, setDecimalSeparator] = useState('.');
  const [hasHeader, setHasHeader] = useState(true);
  const [encoding, setEncoding] = useState(detectedSettings?.encoding || 'utf-8');

  const handleConfirm = () => {
    onConfirm({
      delimiter,
      decimalSeparator,
      hasHeader,
      encoding,
      fileType
    });
  };

  return (
    <div className="fixed inset-0 z-60 flex items-center justify-center">
      <div 
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />
      
      <div className="relative bg-white rounded-xl shadow-2xl w-[480px] max-w-[90vw]">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-800">
            Configuration {fileType.toUpperCase()}
          </h3>
          <button
            onClick={onClose}
            className="w-8 h-8 flex items-center justify-center text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        <div className="p-6 space-y-5">
          {detectedSettings && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
              <h4 className="text-sm font-semibold text-blue-800 mb-2">Paramètres détectés automatiquement</h4>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">Encodage:</span>
                  <span className="ml-2 font-medium text-blue-700">{detectedSettings.encoding}</span>
                </div>
                <div>
                  <span className="text-gray-600">Séparateur:</span>
                  <span className="ml-2 font-medium text-blue-700">'{detectedSettings.delimiter}'</span>
                </div>
                <div>
                  <span className="text-gray-600">Colonnes:</span>
                  <span className="ml-2 font-medium text-blue-700">{detectedSettings.columns}</span>
                </div>
                <div>
                  <span className="text-gray-600">Lignes:</span>
                  <span className="ml-2 font-medium text-blue-700">~{detectedSettings.rows}</span>
                </div>
              </div>
            </div>
          )}

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Séparateur
            </label>
            <select
              value={delimiter}
              onChange={(e) => setDelimiter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#0056D2] focus:border-transparent"
            >
              <option value=",">Virgule (,)</option>
              <option value=";">Point-virgule (;)</option>
              <option value="\t">Tabulation</option>
              <option value="|">Pipe (|)</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Séparateur décimal
            </label>
            <select
              value={decimalSeparator}
              onChange={(e) => setDecimalSeparator(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#0056D2] focus:border-transparent"
            >
              <option value=".">Point (.)</option>
              <option value=",">Virgule (,)</option>
            </select>
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="hasHeader"
              checked={hasHeader}
              onChange={(e) => setHasHeader(e.target.checked)}
              className="w-4 h-4 text-[#0056D2] bg-gray-100 border-gray-300 rounded focus:ring-[#0056D2] focus:ring-2"
            />
            <label htmlFor="hasHeader" className="ml-2 text-sm text-gray-700 font-medium">
              La première ligne contient les en-têtes de colonnes
            </label>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Encodage
            </label>
            <select
              value={encoding}
              onChange={(e) => setEncoding(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#0056D2] focus:border-transparent"
            >
              <option value="utf-8">UTF-8</option>
              <option value="latin-1">Latin-1</option>
              <option value="cp1252">Windows-1252</option>
            </select>
          </div>
        </div>

        <div className="flex justify-end gap-3 px-6 py-4 bg-gray-50 border-t border-gray-200 rounded-b-xl">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors font-medium"
          >
            Annuler
          </button>
          <button
            onClick={handleConfirm}
            className="px-4 py-2 bg-[#0056D2] text-white rounded-lg hover:bg-[#0046b2] transition-colors font-medium"
          >
            Confirmer
          </button>
        </div>
      </div>
    </div>
  );
}

// Modal de prévisualisation des données
interface DataPreviewModalProps {
  data: any[];
  fileName: string;
  onClose: () => void;
  onConfirm: () => void;
}

function DataPreviewModal({ data, fileName, onClose, onConfirm }: DataPreviewModalProps) {
  if (!data || data.length === 0) return null;

  const columns = Object.keys(data[0]);
  const maxRows = 10; // Limiter l'affichage aux 10 premières lignes

  return (
    <div className="fixed inset-0 z-60 flex items-center justify-center">
      <div 
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />
      
      <div className="relative bg-white rounded-xl shadow-2xl w-[90vw] max-w-[1000px] max-h-[90vh] flex flex-col">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 flex-shrink-0">
          <h3 className="text-lg font-semibold text-gray-800">
            Prévisualisation: {fileName}
          </h3>
          <button
            onClick={onClose}
            className="w-8 h-8 flex items-center justify-center text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        <div className="flex-1 overflow-hidden flex flex-col">
          <div className="px-6 py-3 bg-gray-50 border-b border-gray-200">
            <p className="text-sm text-gray-600 font-medium">
              {data.length} lignes affichées sur {data.length} total • {columns.length} colonnes
            </p>
          </div>

          <div className="flex-1 overflow-auto p-6">
            <div className="overflow-x-auto">
              <table className="min-w-full border border-gray-300">
                <thead className="bg-gray-50">
                  <tr>
                    {columns.map((column) => (
                      <th
                        key={column}
                        className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider border-b border-gray-300"
                      >
                        {column}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {data.slice(0, maxRows).map((row, index) => (
                    <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                      {columns.map((column) => (
                        <td
                          key={column}
                          className="px-4 py-3 text-sm text-gray-900 border-b border-gray-200"
                        >
                          {String(row[column])}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div className="flex justify-end gap-3 px-6 py-4 bg-gray-50 border-t border-gray-200 flex-shrink-0">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors font-medium"
          >
            Annuler
          </button>
          <button
            onClick={onConfirm}
            className="px-4 py-2 bg-[#FF6B00] text-white rounded-lg hover:bg-[#e56100] transition-colors font-medium"
          >
            Confirmer le chargement
          </button>
        </div>
      </div>
    </div>
  );
}

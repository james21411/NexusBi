import { useState, useEffect } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { TopMenuBar } from './TopMenuBar';
import { Sidebar } from './Sidebar';
import { Database, Cloud, Server, HardDrive, Plus, RefreshCw, AlertCircle, CheckCircle, Eye, X, Trash2 } from 'lucide-react';
import { getDataSources, syncDataSource, type DataSource, type DataSourceCreate } from '../api/service';
import { API_BASE_URL } from '../api/config';
import { useAuth } from '../api/authContext';
import { SqlImportModal } from './SqlImportModal';

interface DataSourcesViewProps {
  currentView?: string;
  onViewChange?: (view: string) => void;
  onShowImportModal?: () => void;
}

const getIconForType = (type: string) => {
  const iconMap: { [key: string]: any } = {
    'MySQL': Database,
    'PostgreSQL': Server,
    'SQL Server': HardDrive,
    'MongoDB': Database,
    'Cloud': Cloud,
    'API': Cloud,
    'csv': Database,
    'excel': Database,
  };
  return iconMap[type] || Database;
};

const getStatusFromDataSource = (dataSource: DataSource) => {
  // For now, we'll simulate status based on activity and updated_at
  const now = new Date();
  const updatedAt = new Date(dataSource.updated_at);
  const hoursDiff = (now.getTime() - updatedAt.getTime()) / (1000 * 60 * 60);
  
  if (!dataSource.is_active) return 'En pause';
  if (hoursDiff > 48) return 'Erreur';
  return 'Connecté';
};

const getLastSyncFromDate = (dateString: string) => {
  const now = new Date();
  const date = new Date(dateString);
  const diffHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);
  
  if (diffHours < 1) return 'Il y a moins d\'1h';
  if (diffHours < 24) return `Il y a ${Math.floor(diffHours)}h`;
  if (diffHours < 48) return 'Il y a 1j';
  return `Il y a ${Math.floor(diffHours / 24)}j`;
};

const getVolumeFromDataSource = (dataSource: DataSource) => {
  // For now, simulate volume data
  const volumeMap: { [key: string]: string } = {
    'MySQL': '1.2M lignes',
    'PostgreSQL': '3.4M lignes',
    'SQL Server': '2.1M lignes',
    'MongoDB': '5.8M documents',
    'Cloud': '850K lignes',
    'API': '420K enregistrements',
  };
  return volumeMap[dataSource.type] || 'N/A';
};

const getColorForType = (type: string) => {
  const colorMap: { [key: string]: string } = {
    'MySQL': 'bg-blue-500',
    'PostgreSQL': 'bg-indigo-500',
    'SQL Server': 'bg-gray-500',
    'MongoDB': 'bg-green-500',
    'Cloud': 'bg-sky-500',
    'API': 'bg-purple-500',
    'csv': 'bg-orange-500',
    'excel': 'bg-yellow-500',
  };
  return colorMap[type] || 'bg-gray-500';
};

export function DataSourcesView({ currentView, onViewChange, onShowImportModal }: DataSourcesViewProps) {
  const [dataSources, setDataSources] = useState<DataSource[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [syncingDataSources, setSyncingDataSources] = useState<Set<number>>(new Set());
  const [showImportModal, setShowImportModal] = useState(false);
  const [showDataPreview, setShowDataPreview] = useState(false);
  const [previewData, setPreviewData] = useState<{
    rows: any[];
    totalRows: number;
    schema?: any;
    dataSource?: DataSource;
  } | null>(null);
  const [previewSourceName, setPreviewSourceName] = useState('');
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [dataSourceToDelete, setDataSourceToDelete] = useState<DataSource | null>(null);
  const [deletingDataSources, setDeletingDataSources] = useState<Set<number>>(new Set());
  const { token: authToken } = useAuth();

  const handleShowImportModal = () => {
    setShowImportModal(true);
  };

  const handleCloseImportModal = () => {
    setShowImportModal(false);
  };

  const handleViewData = async (dataSource: DataSource) => {
    try {
      // Récupérer les informations du schéma d'abord
      let schemaInfo = null;
      if (dataSource.schema_info) {
        try {
          schemaInfo = JSON.parse(dataSource.schema_info);
        } catch (e) {
          console.warn('Could not parse schema info');
        }
      }

      // Récupérer les données réelles depuis le backend
      const response = await fetch(`${API_BASE_URL}/data-sources/${dataSource.id}/data?limit=100`, {
        headers: authToken ? { Authorization: `Bearer ${authToken}` } : {},
      });

      if (!response.ok) {
        console.error('Erreur lors de la récupération des données');
        return;
      }

      const result = await response.json();
      setPreviewData({
        rows: result.rows || [],
        totalRows: result.total_rows || result.rows?.length || 0,
        schema: schemaInfo,
        dataSource: dataSource
      });
      setPreviewSourceName(dataSource.name);
      setShowDataPreview(true);
    } catch (error) {
      console.error('Erreur lors de la récupération des données:', error);
    }
  };

  const handleCloseDataPreview = () => {
    setShowDataPreview(false);
    setPreviewData(null);
    setPreviewSourceName('');
  };

  const loadDataSources = async () => {
    console.log('Chargement des sources de données depuis la base de données...');

    try {
      setLoading(true);
      setError(null);

      // Utiliser l'API backend
      const result = await getDataSources(null);

      if (result.error) {
        console.error('Erreur API:', result.error);
        setError('Erreur de connexion à la base de données');
        setDataSources([]); // Base vide si erreur
      } else {
        setDataSources(result.data || []);
        console.log('Sources chargées:', result.data?.length || 0);
      }
    } catch (err) {
      console.error('Erreur:', err);
      setError('Erreur lors du chargement des sources de données');
      setDataSources([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSyncDataSource = async (dataSourceId: number) => {
    if (!authToken) return;
    
    setSyncingDataSources(prev => new Set([...prev, dataSourceId]));
    
    try {
      const result = await syncDataSource(dataSourceId, authToken);
      
      if (result.error) {
        console.error('Erreur lors de la synchronisation:', result.error);
      } else {
        // Refresh the data sources list after successful sync
        await loadDataSources();
      }
    } catch (err) {
      console.error('Erreur lors de la synchronisation:', err);
    } finally {
      setSyncingDataSources(prev => {
        const newSet = new Set(prev);
        newSet.delete(dataSourceId);
        return newSet;
      });
    }
  };

  const handleRefreshAll = async () => {
    await loadDataSources();
  };

  const handleDeleteDataSource = async (dataSource: DataSource) => {
    setDataSourceToDelete(dataSource);
    setShowDeleteConfirm(true);
  };

  const confirmDeleteDataSource = async () => {
    if (!dataSourceToDelete) return;

    setDeletingDataSources(prev => new Set([...prev, dataSourceToDelete.id]));

    try {
      const response = await fetch(`${API_BASE_URL}/data-sources/${dataSourceToDelete.id}`, {
        method: 'DELETE',
        headers: authToken ? { Authorization: `Bearer ${authToken}` } : {},
      });

      if (!response.ok) {
        console.error('Erreur lors de la suppression');
        return;
      }

      console.log('Source de données supprimée:', dataSourceToDelete.name);
      // Recharger la liste
      await loadDataSources();

    } catch (error) {
      console.error('Erreur lors de la suppression:', error);
    } finally {
      setDeletingDataSources(prev => {
        const newSet = new Set(prev);
        newSet.delete(dataSourceToDelete.id);
        return newSet;
      });
      setShowDeleteConfirm(false);
      setDataSourceToDelete(null);
    }
  };

  const cancelDeleteDataSource = () => {
    setShowDeleteConfirm(false);
    setDataSourceToDelete(null);
  };

  useEffect(() => {
    loadDataSources();
  }, [authToken]);

  // Calculate statistics
  const activeSources = dataSources.filter(ds => getStatusFromDataSource(ds) === 'Connecté');
  const errorSources = dataSources.filter(ds => getStatusFromDataSource(ds) === 'Erreur');
  const pausedSources = dataSources.filter(ds => getStatusFromDataSource(ds) === 'En pause');
  
  // Simulate total data volume
  const totalVolume = '13.8M lignes';
  
  // Get the most recent sync
  const mostRecentSync = dataSources.length > 0
    ? dataSources.reduce((mostRecent, ds) => {
        if (!ds.updated_at) return mostRecent;
        const dsDate = new Date(ds.updated_at);
        return isNaN(dsDate.getTime()) ? mostRecent : (dsDate > mostRecent ? dsDate : mostRecent);
      }, new Date(dataSources[0].updated_at || Date.now()))
    : new Date();
  
  const timeAgo = getLastSyncFromDate(mostRecentSync.toISOString());

  return (
    <div className="flex flex-col h-screen">
      <TopMenuBar 
        currentView={currentView} 
        onViewChange={onViewChange}
        onShowImportModal={onShowImportModal}
      />
      
      <div className="flex flex-1 overflow-hidden bg-gray-50">
        <Sidebar activeView="data-sources" onNavigate={onViewChange} />
        
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* En-tête */}
          <div className="bg-white border-b border-gray-200 px-4 py-3">
            <div className="flex items-center justify-between mb-1">
              <h1 className="text-gray-800 text-lg">Sources de Données</h1>
              <div className="flex gap-2">
                <button 
                  onClick={handleRefreshAll}
                  disabled={loading}
                  className="px-3 py-1.5 border border-gray-300 text-gray-700 rounded hover:bg-gray-50 transition-colors flex items-center gap-1.5 text-sm disabled:opacity-50"
                >
                  <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
                  Actualiser tout
                </button>
                <button 
                  onClick={handleShowImportModal}
                  className="px-3 py-1.5 bg-[#0056D2] text-white rounded hover:bg-[#0046b2] transition-colors flex items-center gap-1.5 text-sm"
                >
                  <Plus size={14} />
                  Nouvelle source
                </button>
              </div>
            </div>
            <p className="text-gray-600 text-sm">Gérez vos connexions aux sources de données</p>
          </div>

          {/* Statistiques */}
          <div className="bg-white border-b border-gray-200 px-4 py-2">
            <div className="grid grid-cols-4 gap-4">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-green-100 rounded flex items-center justify-center">
                  <CheckCircle size={16} className="text-green-600" />
                </div>
                <div>
                  <p className="text-gray-600 text-sm">Actives</p>
                  <p className="text-gray-800 text-sm">{activeSources.length} sources</p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-red-100 rounded flex items-center justify-center">
                  <AlertCircle size={16} className="text-red-600" />
                </div>
                <div>
                  <p className="text-gray-600 text-sm">Erreurs</p>
                  <p className="text-gray-800 text-sm">{errorSources.length} source</p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-orange-100 rounded flex items-center justify-center">
                  <Database size={16} className="text-[#FF6B00]" />
                </div>
                <div>
                  <p className="text-gray-600 text-sm">Total données</p>
                  <p className="text-gray-800 text-sm">{totalVolume}</p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-blue-100 rounded flex items-center justify-center">
                  <RefreshCw size={16} className="text-[#0056D2]" />
                </div>
                <div>
                  <p className="text-gray-600 text-sm">Dernière sync</p>
                  <p className="text-gray-800 text-sm">{timeAgo}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Liste des sources */}
          <div className="flex-1 overflow-auto p-4">
            {error && (
              <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
                <div className="flex items-center gap-2">
                  <AlertCircle size={16} className="text-red-600" />
                  <p className="text-red-800 text-sm">{error}</p>
                </div>
              </div>
            )}

            {loading ? (
              <div className="flex items-center justify-center h-32">
                <RefreshCw size={24} className="animate-spin text-[#0056D2]" />
                <span className="ml-2 text-gray-600">Chargement des sources de données...</span>
              </div>
            ) : dataSources.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-32 text-gray-500">
                <Database size={48} className="mb-2" />
                <p>Aucune source de données trouvée</p>
                <p className="text-sm">Créez votre première source de données pour commencer</p>
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-4">
                {dataSources.map((source) => {
                  const Icon = getIconForType(source.type);
                  const status = getStatusFromDataSource(source);
                  const isError = status === 'Erreur';
                  const isPaused = status === 'En pause';
                  const isSyncing = syncingDataSources.has(source.id);

                  return (
                    <div
                      key={source.id}
                      className="bg-white border border-gray-200 rounded p-4 hover:shadow transition-shadow"
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-start gap-3">
                          <div className={`w-10 h-10 ${getColorForType(source.type)} rounded flex items-center justify-center`}>
                            <Icon size={20} className="text-white" />
                          </div>

                          <div>
                            <h3 className="text-gray-800 text-sm mb-0.5">{source.name}</h3>
                            <p className="text-gray-600 text-xs">{source.type}</p>
                            {source.schema_info && (() => {
                              try {
                                const schema = JSON.parse(source.schema_info);
                                if (schema.processing_info) {
                                  const { detected_encoding, detected_delimiter } = schema.processing_info;
                                  return (
                                    <p className="text-gray-500 text-xs">
                                      {detected_encoding && `Encodage: ${detected_encoding}`}
                                      {detected_encoding && detected_delimiter && ' • '}
                                      {detected_delimiter && `Séparateur: '${detected_delimiter}'`}
                                    </p>
                                  );
                                }
                              } catch (e) {}
                              return null;
                            })()}
                          </div>
                        </div>

                        <span className={`px-2 py-0.5 rounded-full text-white text-xs ${
                          isError ? 'bg-red-500' :
                          isPaused ? 'bg-orange-500' :
                          'bg-green-500'
                        }`}>
                          {status}
                        </span>
                      </div>

                      <div className="grid grid-cols-2 gap-3 mb-3 text-gray-600 text-xs">
                        <div>
                          <p className="mb-0.5">Dernière sync</p>
                          <p className="text-gray-800">{source.updated_at ? getLastSyncFromDate(source.updated_at) : 'N/A'}</p>
                        </div>
                        <div>
                          <p className="mb-0.5">Volume</p>
                          <p className="text-gray-800">{getVolumeFromDataSource(source)}</p>
                        </div>
                      </div>

                      <div className="flex gap-1.5">
                        <button
                          onClick={() => handleSyncDataSource(source.id)}
                          disabled={isSyncing}
                          className="flex-1 px-3 py-1.5 bg-[#0056D2] text-white rounded hover:bg-[#0046b2] transition-colors flex items-center justify-center gap-1.5 text-xs disabled:opacity-50"
                        >
                          <RefreshCw size={12} className={isSyncing ? 'animate-spin' : ''} />
                          {isSyncing ? 'Synchronisation...' : 'Synchroniser'}
                        </button>
                        <button
                          onClick={() => handleViewData(source)}
                          className="px-3 py-1.5 border border-gray-300 text-gray-700 rounded hover:bg-gray-50 transition-colors text-xs flex items-center gap-1"
                          title="Visualiser les données"
                        >
                          <Eye size={12} />
                        </button>
                        <button
                          onClick={() => handleDeleteDataSource(source)}
                          disabled={deletingDataSources.has(source.id)}
                          className="px-3 py-1.5 border border-red-300 text-red-700 rounded hover:bg-red-50 transition-colors text-xs flex items-center gap-1 disabled:opacity-50"
                          title="Supprimer la source"
                        >
                          <Trash2 size={12} />
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Modale d'import */}
      {showImportModal && (
        <SqlImportModal 
          onClose={handleCloseImportModal}
          onDataSourceCreated={loadDataSources}
        />
      )}

      {/* Modale de prévisualisation des données */}
      {showDataPreview && previewData && (
        <DataPreviewModal
          data={previewData.rows}
          totalRows={previewData.totalRows}
          schema={previewData.schema}
          dataSource={previewData.dataSource}
          fileName={previewSourceName}
          onClose={handleCloseDataPreview}
          onConfirm={handleCloseDataPreview}
        />
      )}

      {/* Modale de confirmation de suppression */}
      {showDeleteConfirm && dataSourceToDelete && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div
            className="absolute inset-0 bg-black/50 backdrop-blur-sm"
            onClick={cancelDeleteDataSource}
          />

          <div className="relative bg-white rounded-xl shadow-2xl w-[400px] max-w-[90vw]">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-800">
                Confirmer la suppression
              </h3>
              <button
                onClick={cancelDeleteDataSource}
                className="w-8 h-8 flex items-center justify-center text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X size={20} />
              </button>
            </div>

            <div className="p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                  <Trash2 size={24} className="text-red-600" />
                </div>
                <div>
                  <p className="text-gray-800 font-medium">
                    Supprimer "{dataSourceToDelete.name}" ?
                  </p>
                  <p className="text-gray-600 text-sm">
                    Cette action est irréversible. Toutes les données associées seront supprimées.
                  </p>
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-3 px-6 py-4 bg-gray-50 border-t border-gray-200 rounded-b-xl">
              <button
                onClick={cancelDeleteDataSource}
                className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
              >
                Annuler
              </button>
              <button
                onClick={confirmDeleteDataSource}
                disabled={deletingDataSources.has(dataSourceToDelete.id)}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {deletingDataSources.has(dataSourceToDelete.id) ? 'Suppression...' : 'Supprimer'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Modal de prévisualisation des données (réutilisable)
interface DataPreviewModalProps {
  data: any[];
  totalRows?: number;
  schema?: any;
  dataSource?: DataSource;
  fileName: string;
  onClose: () => void;
  onConfirm: () => void;
}

function DataPreviewModal({ data, totalRows, schema, dataSource, fileName, onClose, onConfirm }: DataPreviewModalProps) {
  const [showOptions, setShowOptions] = useState(false);
  const [displayMode, setDisplayMode] = useState<'first' | 'last' | 'range'>('first');
  const [rowCount, setRowCount] = useState(50);
  const [startRow, setStartRow] = useState(0);
  const [endRow, setEndRow] = useState(49);
  const [visibleColumns, setVisibleColumns] = useState<string[]>([]);
  const [searchTerm, setSearchTerm] = useState('');

  // Initialize visible columns
  useEffect(() => {
    if (data && data.length > 0) {
      const allColumns = Object.keys(data[0]);
      setVisibleColumns(allColumns);
    }
  }, [data]);

  if (!data || data.length === 0) return null;

  const allColumns = Object.keys(data[0]);

  // Filter and slice data based on current settings
  let displayData = [...data];

  // Apply row filtering
  if (displayMode === 'first') {
    displayData = displayData.slice(0, rowCount);
  } else if (displayMode === 'last') {
    displayData = displayData.slice(-rowCount);
  } else if (displayMode === 'range') {
    displayData = displayData.slice(startRow, endRow + 1);
  }

  // Apply column filtering
  const filteredColumns = allColumns.filter(col => visibleColumns.includes(col));

  // Apply search filtering
  if (searchTerm) {
    displayData = displayData.filter(row =>
      filteredColumns.some(col =>
        String(row[col]).toLowerCase().includes(searchTerm.toLowerCase())
      )
    );
  }

  const toggleColumn = (column: string) => {
    setVisibleColumns(prev =>
      prev.includes(column)
        ? prev.filter(c => c !== column)
        : [...prev, column]
    );
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />

      <div className="relative bg-white rounded-xl shadow-2xl w-[90vw] max-w-[1000px] max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 flex-shrink-0">
          <div className="flex items-center gap-4">
            <h3 className="text-lg font-medium text-gray-800">
              Données: {fileName}
            </h3>
            <div className="text-sm text-gray-500">
              {totalRows ? `${totalRows} lignes totales` : `${data.length} lignes chargées`}
              {schema?.column_count && ` • ${schema.column_count} colonnes`}
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowOptions(!showOptions)}
              className="px-3 py-1.5 border border-gray-300 text-gray-700 rounded hover:bg-gray-50 transition-colors text-sm flex items-center gap-1"
            >
              ⚙️ Options
            </button>
            <button
              onClick={onClose}
              className="w-8 h-8 flex items-center justify-center text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X size={20} />
            </button>
          </div>
        </div>

        {/* Options Panel */}
        {showOptions && (
          <div className="border-b border-gray-200 bg-gray-50 p-4 flex-shrink-0">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Row Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Lignes à afficher
                </label>
                <div className="space-y-2">
                  <select
                    value={displayMode}
                    onChange={(e) => setDisplayMode(e.target.value as any)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                  >
                    <option value="first">Premières lignes</option>
                    <option value="last">Dernières lignes</option>
                    <option value="range">Plage personnalisée</option>
                  </select>

                  {displayMode === 'range' ? (
                    <div className="flex gap-2">
                      <input
                        type="number"
                        placeholder="Début"
                        value={startRow}
                        onChange={(e) => setStartRow(Math.max(0, parseInt(e.target.value) || 0))}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm"
                      />
                      <input
                        type="number"
                        placeholder="Fin"
                        value={endRow}
                        onChange={(e) => setEndRow(Math.max(startRow, parseInt(e.target.value) || 0))}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm"
                      />
                    </div>
                  ) : (
                    <input
                      type="number"
                      placeholder="Nombre de lignes"
                      value={rowCount}
                      onChange={(e) => setRowCount(Math.max(1, parseInt(e.target.value) || 10))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                    />
                  )}
                </div>
              </div>

              {/* Column Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Colonnes ({visibleColumns.length}/{allColumns.length} visibles)
                </label>
                <div className="max-h-32 overflow-y-auto border border-gray-300 rounded-lg p-2">
                  {allColumns.map(column => (
                    <label key={column} className="flex items-center gap-2 text-sm">
                      <input
                        type="checkbox"
                        checked={visibleColumns.includes(column)}
                        onChange={() => toggleColumn(column)}
                        className="rounded"
                      />
                      {column}
                    </label>
                  ))}
                </div>
              </div>

              {/* Search */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Rechercher
                </label>
                <input
                  type="text"
                  placeholder="Rechercher dans les données..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                />
              </div>
            </div>
          </div>
        )}

        {/* Data Table */}
        <div className="flex-1 overflow-hidden flex flex-col">
          <div className="px-6 py-2 bg-gray-50 border-b border-gray-200 text-sm text-gray-600">
            Affichage de {displayData.length} lignes • {filteredColumns.length} colonnes
            {searchTerm && ` • Recherche: "${searchTerm}"`}
          </div>

          <div className="flex-1 overflow-auto">
            <div className="inline-block min-w-full">
              <table className="min-w-full border border-gray-300">
                <thead className="bg-gray-50 sticky top-0">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-b border-gray-300 bg-gray-50">
                      #
                    </th>
                    {filteredColumns.map((column) => (
                      <th
                        key={column}
                        className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-b border-gray-300 bg-gray-50"
                      >
                        {column}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {displayData.map((row, index) => (
                    <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                      <td className="px-4 py-3 text-sm text-gray-500 border-b border-gray-200 font-mono">
                        {(displayMode === 'first' ? index :
                          displayMode === 'last' ? (data.length - rowCount + index) :
                          startRow + index) + 1}
                      </td>
                      {filteredColumns.map((column) => (
                        <td
                          key={column}
                          className="px-4 py-3 text-sm text-gray-900 border-b border-gray-200 max-w-xs truncate"
                          title={String(row[column])}
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

        {/* Footer */}
        <div className="flex justify-between items-center px-6 py-4 bg-gray-50 border-t border-gray-200 flex-shrink-0">
          <div className="text-sm text-gray-600">
            {dataSource?.type && `Type: ${dataSource.type}`}
            {schema?.processing_info?.detected_encoding && ` • Encodage: ${schema.processing_info.detected_encoding}`}
          </div>
          <button
            onClick={onConfirm}
            className="px-4 py-2 bg-[#0056D2] text-white rounded-lg hover:bg-[#0046b2] transition-colors"
          >
            Fermer
          </button>
        </div>
      </div>
    </div>
  );
}
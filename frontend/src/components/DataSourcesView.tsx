import { useState, useEffect, useMemo, useCallback } from 'react';
import { Database, Cloud, Server, HardDrive, Plus, RefreshCw, AlertCircle, CheckCircle, Eye, X, Trash2 } from 'lucide-react';
import { TopMenuBar } from './TopMenuBar';
import { Sidebar } from './Sidebar';
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
  // Improved error detection logic - only show errors for real issues
  const now = new Date();
  const updatedAt = dataSource.updated_at ? new Date(dataSource.updated_at) : null;
  const hoursDiff = updatedAt ? (now.getTime() - updatedAt.getTime()) / (1000 * 60 * 60) : null;
  
  if (!dataSource.is_active) return { status: 'En pause', isError: false, errorTooltip: null };
  
  // Only mark as error if very old (7+ days) AND no recent activity
  if (hoursDiff && hoursDiff > 168) { // 7 days
    return {
      status: 'Erreur',
      isError: true,
      errorTooltip: 'Source inactive depuis plus de 7 jours - vérifiez la connexion'
    };
  }
  
  return { status: 'Connecté', isError: false, errorTooltip: null };
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
  // Use real data from schema_info if available
  if (dataSource.schema_info) {
    try {
      const schema = JSON.parse(dataSource.schema_info);
      
      // For SQL dump files, use total_rows or row_count (both supported now)
      if (dataSource.type === 'sql') {
        const rowCount = schema.total_rows || schema.row_count;
        if (rowCount) {
          if (rowCount >= 1000000) {
            return `${(rowCount / 1000000).toFixed(1)}M lignes`;
          } else if (rowCount >= 1000) {
            return `${(rowCount / 1000).toFixed(1)}K lignes`;
          } else {
            return `${rowCount} lignes`;
          }
        }
      }
      
      // For other file types, use row_count
      if (schema.row_count) {
        const rowCount = schema.row_count;
        if (rowCount >= 1000000) {
          return `${(rowCount / 1000000).toFixed(1)}M lignes`;
        } else if (rowCount >= 1000) {
          return `${(rowCount / 1000).toFixed(1)}K lignes`;
        } else {
          return `${rowCount} lignes`;
        }
      }
    } catch (e) {
      // Fall back to type-based estimation
    }
  }
  
  // Fallback: estimate based on type and last update time
  const typeEstimates: { [key: string]: string } = {
    'MySQL': 'Est. 1.2M lignes',
    'PostgreSQL': 'Est. 3.4M lignes',
    'SQL Server': 'Est. 2.1M lignes',
    'MongoDB': 'Est. 5.8M documents',
    'Cloud': 'Est. 850K lignes',
    'API': 'Est. 420K enregistrements',
    'csv': 'Est. 150K lignes',
    'excel': 'Est. 50K lignes',
    'sql': 'Est. 500K lignes',
  };
  return typeEstimates[dataSource.type] || 'N/A';
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

const getGradientForType = (type: string) => {
  const gradientMap: { [key: string]: string } = {
    'MySQL': 'bg-gradient-to-br from-blue-400 via-blue-500 to-blue-600',
    'PostgreSQL': 'bg-gradient-to-br from-indigo-400 via-indigo-500 to-indigo-600',
    'SQL Server': 'bg-gradient-to-br from-gray-400 via-gray-500 to-gray-600',
    'MongoDB': 'bg-gradient-to-br from-green-400 via-green-500 to-green-600',
    'Cloud': 'bg-gradient-to-br from-sky-400 via-sky-500 to-sky-600',
    'API': 'bg-gradient-to-br from-purple-400 via-purple-500 to-purple-600',
    'csv': 'bg-gradient-to-br from-orange-400 via-orange-500 to-orange-600',
    'excel': 'bg-gradient-to-br from-yellow-400 via-yellow-500 to-yellow-600',
  };
  return gradientMap[type] || 'bg-gradient-to-br from-gray-400 via-gray-500 to-gray-600';
};

export function DataSourcesView({ currentView, onViewChange, onShowImportModal }: DataSourcesViewProps) {
  const [dataSources, setDataSources] = useState<DataSource[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [syncingDataSources, setSyncingDataSources] = useState<Set<number>>(new Set());
  const [showImportModal, setShowImportModal] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [dataSourceToDelete, setDataSourceToDelete] = useState<DataSource | null>(null);
  const [deletingDataSources, setDeletingDataSources] = useState<Set<number>>(new Set());
  const [showSyncModal, setShowSyncModal] = useState(false);
  const [syncSuccess, setSyncSuccess] = useState(false);
  const [syncMessage, setSyncMessage] = useState("");
  const [syncProgress, setSyncProgress] = useState(0);
  const { token: authToken } = useAuth();

  const handleShowImportModal = useCallback(() => {
    setShowImportModal(true);
  }, []);

  const handleCloseImportModal = useCallback(() => {
    setShowImportModal(false);
  }, []);

  const handleViewData = async (dataSource: DataSource) => {
    try {
      console.log(`Lancement de l'interface tkinter pour la source: ${dataSource.name}`);
      
      // Essayer d'abord avec l'endpoint authentifié
      let response;
      try {
        console.log('Tentative avec endpoint authentifié...');
        console.log('Auth token présent:', !!authToken);
        
        response = await fetch(`${API_BASE_URL}/preview/launch-preview/${dataSource.id}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(authToken ? { Authorization: `Bearer ${authToken}` } : {})
          },
          credentials: 'include'
        });

        console.log('Réponse authentifiée:', response.status, response.statusText);
        
        if (response.ok) {
          const result = await response.json();
          console.log('Interface tkinter lancée avec succès:', result);
          alert(`Interface de prévisualisation lancée avec succès. PID: ${result.process_id}`);
          return;
        } else if (response.status === 401) {
          console.log('Non autorisé - passage à l\'endpoint de test');
          throw new Error('Non autorisé');
        }
      } catch (authError) {
        console.log('Erreur d\'authentification, tentative avec l\'endpoint de test...:', authError);
      }

      // Si l'endpoint authentifié échoue, essayer l'endpoint de test
      console.log('Tentative avec l\'endpoint de test...');
      try {
        response = await fetch(`${API_BASE_URL}/preview/test-launch/${dataSource.id}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          }
        });

        console.log('Réponse de test:', response.status, response.statusText);
        
        if (response.ok) {
          const result = await response.json();
          console.log('Test de lancement réussi:', result);
          alert(`Interface de prévisualisation lancée avec succès. PID: ${result.process_id}`);
        } else {
          console.error('Échec du test de lancement:', response.status, response.statusText);
          throw new Error(`Échec du test de lancement: ${response.status} ${response.statusText}`);
        }
      } catch (testError) {
        console.error('Erreur lors du test de lancement:', testError);
        throw testError;
      }
      
    } catch (error) {
     console.error('Erreur lors du lancement de l\'interface tkinter:', error);
    
     // Proposer une solution alternative
     const errorMessage = error instanceof Error ? error.message : String(error);
     const useDemo = confirm(
       `Erreur lors du lancement de l'interface de prévisualisation: ${errorMessage}\n\n` +
       'Cela peut être dû à un problème de configuration X11 ou à l\'absence de la variable DISPLAY.\n\n' +
       'Souhaitez-vous lancer la démonstration avec des données fictives ?'
     );
      
      if (useDemo) {
        try {
          // Lancer directement le script de démonstration
          const demoResponse = await fetch('/api/demo-launch', {
            method: 'POST'
          });
          if (demoResponse.ok) {
            alert('Démonstration lancée avec succès !');
          } else {
            // Fallback: suggérer de lancer manuellement
            alert(
              'Pour tester l\'interface tkinter, exécutez cette commande dans un terminal :\n\n' +
              'python test_tkinter_demo.py\n\n' +
              'Cela ouvrira une fenêtre de démonstration avec des données fictives.'
            );
          }
        } catch (demoError) {
          console.error('Erreur de démonstration:', demoError);
          alert(
            'Pour tester l\'interface tkinter, exécutez cette commande dans un terminal :\n\n' +
            'python test_tkinter_demo.py\n\n' +
            'Cela ouvrira une fenêtre de démonstration avec des données fictives.'
          );
        }
      } else {
       // Si l'utilisateur ne veut pas la démonstration, donner des instructions claires
       alert(
         'Pour résoudre ce problème:\n\n' +
         '1. Vérifiez que vous êtes connecté\n' +
         '2. Assurez-vous que le backend est en cours d\'exécution\n' +
         '3. Vérifiez que X11 est configuré et que la variable DISPLAY est correcte\n' +
         '4. Si vous utilisez Docker, assurez-vous que X11 forwarding est activé\n\n' +
         'Vous pouvez également essayer de lancer manuellement avec:\n' +
         'python test_tkinter_demo.py'
       );
     }
    }
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
    // Suppression temporaire de la vérification d'authentification
    // if (!authToken) {
    //   alert("Vous devez être connecté pour synchroniser les données. Veuillez vous connecter d'abord.");
    //   return;
    // }

    setSyncingDataSources(prev => new Set([...prev, dataSourceId]));
    setShowSyncModal(true);
    setSyncSuccess(false);
    setSyncMessage("Initialisation...");
    setSyncProgress(0);

    try {
      // Simuler une progression pendant la synchronisation
      const progressInterval = setInterval(() => {
        setSyncProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + Math.random() * 20;
        });
      }, 200);

      setSyncMessage("Connexion à la source de données...");

      const result = await syncDataSource(dataSourceId, authToken);
      
      clearInterval(progressInterval);
      setSyncProgress(100);
      
      if (result.error) {
        console.error("Erreur lors de la synchronisation:", result.error);
        setSyncSuccess(false);
        setSyncMessage(`Erreur: ${result.error}`);
      } else {
        console.log("Synchronisation réussie:", result);
        setSyncSuccess(true);
        const rowsUpdated = result.data?.rows_updated || 0;
        setSyncMessage(`Réussi ! ${rowsUpdated} lignes mises à jour`);
        
        // Refresh the data sources list after successful sync
        await loadDataSources();
      }
    } catch (err) {
      console.error("Erreur lors de la synchronisation:", err);
      setSyncSuccess(false);
      setSyncMessage("Erreur de synchronisation");
      setSyncProgress(0);
    } finally {
      setSyncingDataSources(prev => {
        const newSet = new Set(prev);
        newSet.delete(dataSourceId);
        return newSet;
      });
      
      // Auto-close modal after 3 seconds
      setTimeout(() => {
        setShowSyncModal(false);
        setSyncProgress(0);
      }, 3000);
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

  // Calculate statistics with memoization
  const statistics = useMemo(() => {
    const activeSources = dataSources.filter(ds => getStatusFromDataSource(ds).status === 'Connecté');
    const errorSources = dataSources.filter(ds => getStatusFromDataSource(ds).status === 'Erreur');
    const pausedSources = dataSources.filter(ds => getStatusFromDataSource(ds).status === 'En pause');

    // Calculate real total volume from all sources
    const totalRows = dataSources.reduce((total, source) => {
      if (source.schema_info) {
        try {
          const schema = JSON.parse(source.schema_info);
          // For SQL dump files, use total_rows or row_count (both supported now)
          if (source.type === 'sql') {
            const rowCount = schema.total_rows || schema.row_count;
            if (rowCount) {
              return total + rowCount;
            }
          }
          // For other file types, use row_count
          if (schema.row_count) {
            return total + schema.row_count;
          }
        } catch (e) {}
      }
      return total;
    }, 0);

    const formatTotalVolume = (rows: number) => {
      if (rows >= 1000000) {
        return `${(rows / 1000000).toFixed(1)}M lignes`;
      } else if (rows >= 1000) {
        return `${(rows / 1000).toFixed(1)}K lignes`;
      } else {
        return `${rows} lignes`;
      }
    };

    const totalVolume = totalRows > 0 ? formatTotalVolume(totalRows) : '0 lignes';

    // Get the most recent sync
    const mostRecentSync = dataSources.length > 0
      ? dataSources.reduce((mostRecent, ds) => {
          if (!ds.updated_at) return mostRecent;
          const dsDate = new Date(ds.updated_at);
          return isNaN(dsDate.getTime()) ? mostRecent : (dsDate > mostRecent ? dsDate : mostRecent);
        }, new Date(dataSources[0].updated_at || Date.now()))
      : new Date();

    const timeAgo = getLastSyncFromDate(mostRecentSync.toISOString());

    return {
      activeSources,
      errorSources,
      pausedSources,
      totalVolume,
      timeAgo
    };
  }, [dataSources]);

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

          {/* Contenu principal */}
          <div className="flex-1 flex overflow-hidden">
            {/* Liste des sources */}
            <div className="flex-1 flex flex-col border-r border-gray-200 bg-white">
              {/* Statistiques */}
              <div className="bg-white border-b border-gray-200 px-4 py-2 flex-shrink-0">
                <div className="grid grid-cols-4 gap-4">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 bg-green-100 rounded flex items-center justify-center">
                      <CheckCircle size={16} className="text-green-600" />
                    </div>
                    <div>
                      <p className="text-gray-600 text-sm">Actives</p>
                      <p className="text-gray-800 text-sm">{statistics.activeSources.length} sources</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 bg-red-100 rounded flex items-center justify-center">
                      <AlertCircle size={16} className="text-red-600" />
                    </div>
                    <div>
                      <p className="text-gray-600 text-sm">Erreurs</p>
                      <p className="text-gray-800 text-sm">{statistics.errorSources.length} source</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 bg-orange-100 rounded flex items-center justify-center">
                      <Database size={16} className="text-[#FF6B00]" />
                    </div>
                    <div>
                      <p className="text-gray-600 text-sm">Total données</p>
                      <p className="text-gray-800 text-sm">{statistics.totalVolume}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 bg-blue-100 rounded flex items-center justify-center">
                      <RefreshCw size={16} className="text-[#0056D2]" />
                    </div>
                    <div>
                      <p className="text-gray-600 text-sm">Dernière sync</p>
                      <p className="text-gray-800 text-sm">{statistics.timeAgo}</p>
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
                  <div className="grid grid-cols-4 md:grid-cols-5 lg:grid-cols-6 gap-3">
                    {dataSources.map((source) => {
                      const Icon = getIconForType(source.type);
                      const statusInfo = getStatusFromDataSource(source);
                      const isError = statusInfo.isError;
                      const isPaused = statusInfo.status === 'En pause';
                      const isSyncing = syncingDataSources.has(source.id);

                      return (
                        <div
                          key={source.id}
                          className="relative overflow-hidden bg-white border rounded-lg p-4 hover:shadow-lg hover:scale-[1.02] transition-all duration-300 cursor-pointer min-h-[180px] flex flex-col animate-in fade-in slide-in-from-bottom-2 border-gray-200"
                          style={{ animationDelay: `${(dataSources.indexOf(source) % 12) * 50}ms` }}
                        >
                          {/* Background gradient overlay */}
                          <div className={`absolute inset-0 opacity-5 ${getGradientForType(source.type)}`} />
                          {/* Subtle pattern overlay */}
                          <div className="absolute inset-0 opacity-10 bg-gradient-to-br from-transparent via-white to-transparent" />

                          {/* Content */}
                          <div className="relative z-10">
                            <div className="flex items-start justify-between mb-4">
                              <div className="flex items-start gap-3 flex-1 min-w-0">
                                <div className={`w-12 h-12 ${getColorForType(source.type)} rounded-lg flex items-center justify-center shadow-sm`}>
                                  <Icon size={24} className="text-white" />
                                </div>

                                <div className="flex-1 min-w-0">
                                  <h3 className="text-gray-900 text-sm font-medium mb-1 truncate">{source.name}</h3>
                                  <p className="text-gray-600 text-xs mb-1">{source.type}</p>
                                  {source.schema_info && (() => {
                                    try {
                                      const schema = JSON.parse(source.schema_info);
                                      if (schema.processing_info) {
                                        const { detected_encoding, detected_delimiter } = schema.processing_info;
                                        return (
                                          <p className="text-gray-500 text-xs truncate">
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

                              <div className="flex flex-col items-end gap-2 ml-2">
                                <div className="relative">
                                  <span className={`px-2 py-1 rounded-full text-white text-xs font-medium ${
                                    isError ? 'bg-red-500' :
                                    isPaused ? 'bg-orange-500' :
                                    'bg-green-500'
                                  }`}>
                                    {statusInfo.status}
                                  </span>
                                  {/* Error tooltip */}
                                  {isError && statusInfo.errorTooltip && (
                                    <div className="absolute right-0 top-full mt-1 w-64 p-2 bg-red-100 border border-red-200 rounded-md text-xs text-red-800 shadow-lg z-20 opacity-0 hover:opacity-100 transition-opacity pointer-events-none">
                                      {statusInfo.errorTooltip}
                                    </div>
                                  )}
                                </div>
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleDeleteDataSource(source);
                                  }}
                                  disabled={deletingDataSources.has(source.id)}
                                  className="p-1.5 text-red-500 hover:bg-red-50 rounded-md transition-colors disabled:opacity-50"
                                  title="Supprimer la source"
                                >
                                  <Trash2 size={16} />
                                </button>
                              </div>
                            </div>

                            <div className="grid grid-cols-2 gap-4 mb-4 text-gray-600 text-xs">
                              <div className="bg-gray-50 rounded-md p-2">
                                <p className="text-gray-500 mb-1 font-medium">Dernière sync</p>
                                <p className="text-gray-800 font-medium">{source.updated_at ? getLastSyncFromDate(source.updated_at) : 'N/A'}</p>
                              </div>
                              <div className="bg-gray-50 rounded-md p-2">
                                <p className="text-gray-500 mb-1 font-medium">Volume</p>
                                <p className="text-gray-800 font-medium">{getVolumeFromDataSource(source)}</p>
                              </div>
                            </div>

                            <div className="flex gap-2 mt-auto">
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleSyncDataSource(source.id);
                                }}
                                disabled={isSyncing}
                                className="flex-1 px-3 py-2 bg-[#0056D2] text-white rounded-lg hover:bg-[#0046b2] transition-all duration-200 flex items-center justify-center gap-2 text-sm font-medium disabled:opacity-50 shadow-sm hover:shadow-md" title="Synchronise les données depuis la source externe et met à jour le cache local avec les dernières informations (volume, structure, données)"
                              >
                                <RefreshCw size={14} className={isSyncing ? 'animate-spin' : ''} />
                                {isSyncing ? 'Synchronisation...' : 'Synchroniser'}
                              </button>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleViewData(source);
                                }}
                                className="px-3 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-all duration-200 text-sm font-medium flex items-center gap-2 shadow-sm hover:shadow-md"
                              >
                                <Eye size={14} />
                                Voir
                              </button>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>
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

      {/* Modal de synchronisation compact */}
      {showSyncModal && (
        <div className="fixed top-4 right-4 z-50">
          <div className={`relative bg-white rounded-lg shadow-xl border-2 w-80 ${
            syncSuccess ? "border-green-200" : "border-blue-200"
          }`}>
            <div className="p-4">
              {syncSuccess ? (
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                    <CheckCircle size={20} className="text-green-600" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-green-800">Synchronisation réussie</p>
                    <p className="text-xs text-green-600">{syncMessage}</p>
                  </div>
                </div>
              ) : (
                <div>
                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                      <RefreshCw size={20} className="text-blue-600 animate-spin" />
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-blue-800">Synchronisation</p>
                      <p className="text-xs text-blue-600">{syncMessage}</p>
                    </div>
                    <div className="text-xs font-medium text-blue-600">
                      {Math.round(syncProgress)}%
                    </div>
                  </div>
                  
                  {/* Barre de progression */}
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300 ease-out"
                      style={{ width: `${syncProgress}%` }}
                    ></div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
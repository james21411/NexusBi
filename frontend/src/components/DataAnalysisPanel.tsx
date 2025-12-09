import { useState, useEffect } from 'react';
import { Code, BarChart2, AlertTriangle, CheckCircle, FileText } from 'lucide-react';
import { analyzeData, generateCleaningCode } from '../api/service';
import { useAuthContext } from '../api/authContext';

interface DataAnalysisPanelProps {
  projectId: number;
  dataSourceId: number;
  onClose?: () => void;
}

interface AnalysisResult {
  missing_values: {
    total_missing: number;
    total_percentage: number;
    columns: Record<string, {
      count: number;
      percentage: number;
      dtype: string;
    }>;
  };
  outliers: Record<string, {
    count: number;
    percentage: number;
  }>;
  duplicates: {
    count: number;
    percentage: number;
  };
}

export function DataAnalysisPanel({ projectId, dataSourceId, onClose }: DataAnalysisPanelProps) {
  const [analysisResults, setAnalysisResults] = useState<AnalysisResult | null>(null);
  const [cleaningCode, setCleaningCode] = useState('');
  const [comprehensiveCode, setComprehensiveCode] = useState('');
  const [visualizationSuggestions, setVisualizationSuggestions] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'analysis' | 'code' | 'visualization'>('analysis');
  const { token: authToken } = useAuthContext();

  const runAnalysis = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Analyze data
      const analysisResponse = await analyzeData(
        projectId,
        dataSourceId,
        'quality',
        'mean',
        authToken
      );

      if (analysisResponse.error) {
        throw new Error(analysisResponse.error);
      }

      if (analysisResponse.data) {
        setAnalysisResults(analysisResponse.data.analysis_results);
        setCleaningCode(analysisResponse.data.cleaning_code);
        setComprehensiveCode(analysisResponse.data.comprehensive_cleaning_code || '');
        setVisualizationSuggestions(analysisResponse.data.visualization_suggestions || []);
      }

      // Generate comprehensive cleaning code
      const codeResponse = await generateCleaningCode(
        projectId,
        dataSourceId,
        'mean',
        authToken
      );

      if (codeResponse.data) {
        setComprehensiveCode(codeResponse.data.comprehensive_cleaning_code || '');
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze data');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    runAnalysis();
  }, [projectId, dataSourceId]);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat().format(num);
  };

  if (isLoading) {
    return (
      <div className="p-4 bg-white rounded-lg shadow">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-8 h-8 bg-blue-600 rounded flex items-center justify-center">
            <BarChart2 size={18} className="text-white" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900">Data Analysis</h3>
        </div>
        <div className="space-y-3">
          <div className="h-4 bg-gray-200 rounded animate-pulse"></div>
          <div className="h-4 bg-gray-200 rounded animate-pulse w-3/4"></div>
          <div className="h-4 bg-gray-200 rounded animate-pulse w-1/2"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
        <div className="flex items-center gap-2 mb-2">
          <AlertTriangle size={18} className="text-red-600" />
          <h3 className="text-lg font-semibold text-red-800">Analysis Error</h3>
        </div>
        <p className="text-red-600">{error}</p>
        <button
          onClick={runAnalysis}
          className="mt-3 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
        >
          Retry Analysis
        </button>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded flex items-center justify-center">
              <BarChart2 size={18} className="text-white" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900">Data Analysis Results</h3>
          </div>
          <div className="flex gap-2">
            <button
              onClick={runAnalysis}
              className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 transition-colors"
              title="Refresh Analysis"
            >
              Refresh
            </button>
            {onClose && (
              <button
                onClick={onClose}
                className="px-3 py-1 bg-gray-200 text-gray-700 rounded text-sm hover:bg-gray-300 transition-colors"
              >
                Close
              </button>
            )}
          </div>
        </div>
      </div>

      <div className="p-4">
        {/* Analysis Tabs */}
        <div className="flex gap-2 mb-4 border-b border-gray-200">
          <button
            onClick={() => setActiveTab('analysis')}
            className={`px-4 py-2 text-sm font-medium ${activeTab === 'analysis' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
          >
            Analysis Results
          </button>
          <button
            onClick={() => setActiveTab('code')}
            className={`px-4 py-2 text-sm font-medium ${activeTab === 'code' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
          >
            Cleaning Code
          </button>
          <button
            onClick={() => setActiveTab('visualization')}
            className={`px-4 py-2 text-sm font-medium ${activeTab === 'visualization' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
          >
            Visualization
          </button>
        </div>

        {/* Analysis Results Tab */}
        {activeTab === 'analysis' && analysisResults && (
          <div className="space-y-6">
            {/* Data Quality Summary */}
            <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
              <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <CheckCircle size={16} className="text-green-600" />
                Data Quality Summary
              </h4>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Missing Values */}
                <div className="bg-white p-3 rounded border border-gray-200">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-6 h-6 bg-red-100 rounded flex items-center justify-center">
                      <AlertTriangle size={14} className="text-red-600" />
                    </div>
                    <h5 className="font-medium text-gray-800">Missing Values</h5>
                  </div>
                  <div className="text-2xl font-bold text-gray-900">
                    {formatNumber(analysisResults.missing_values.total_missing)}
                  </div>
                  <div className="text-sm text-gray-600">
                    {analysisResults.missing_values.total_percentage.toFixed(2)}% of total
                  </div>
                </div>

                {/* Outliers */}
                <div className="bg-white p-3 rounded border border-gray-200">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-6 h-6 bg-yellow-100 rounded flex items-center justify-center">
                      <AlertTriangle size={14} className="text-yellow-600" />
                    </div>
                    <h5 className="font-medium text-gray-800">Outliers</h5>
                  </div>
                  <div className="text-2xl font-bold text-gray-900">
                    {Object.keys(analysisResults.outliers || {}).length}
                  </div>
                  <div className="text-sm text-gray-600">
                    columns affected
                  </div>
                </div>

                {/* Duplicates */}
                <div className="bg-white p-3 rounded border border-gray-200">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-6 h-6 bg-blue-100 rounded flex items-center justify-center">
                      <FileText size={14} className="text-blue-600" />
                    </div>
                    <h5 className="font-medium text-gray-800">Duplicates</h5>
                  </div>
                  <div className="text-2xl font-bold text-gray-900">
                    {formatNumber(analysisResults.duplicates.count)}
                  </div>
                  <div className="text-sm text-gray-600">
                    {analysisResults.duplicates.percentage.toFixed(2)}% of rows
                  </div>
                </div>
              </div>
            </div>

            {/* Missing Values Details */}
            {analysisResults.missing_values.total_missing > 0 && (
              <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <AlertTriangle size={16} className="text-red-600" />
                  Missing Values by Column
                </h4>

                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-100 text-gray-600">
                      <tr>
                        <th className="p-2 text-left">Column</th>
                        <th className="p-2 text-left">Missing Count</th>
                        <th className="p-2 text-left">Percentage</th>
                        <th className="p-2 text-left">Data Type</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(analysisResults.missing_values.columns).map(([col, info]) => (
                        <tr key={col} className="border-t border-gray-100">
                          <td className="p-2 font-medium text-gray-900">{col}</td>
                          <td className="p-2 text-gray-700">{formatNumber(info.count)}</td>
                          <td className="p-2 text-gray-700">{info.percentage.toFixed(2)}%</td>
                          <td className="p-2 text-gray-700">{info.dtype}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Outliers Details */}
            {Object.keys(analysisResults.outliers || {}).length > 0 && (
              <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <AlertTriangle size={16} className="text-yellow-600" />
                  Outliers Detection
                </h4>

                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-100 text-gray-600">
                      <tr>
                        <th className="p-2 text-left">Column</th>
                        <th className="p-2 text-left">Outlier Count</th>
                        <th className="p-2 text-left">Percentage</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(analysisResults.outliers).map(([col, info]) => (
                        <tr key={col} className="border-t border-gray-100">
                          <td className="p-2 font-medium text-gray-900">{col}</td>
                          <td className="p-2 text-gray-700">{formatNumber(info.count)}</td>
                          <td className="p-2 text-gray-700">{info.percentage.toFixed(2)}%</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Cleaning Code Tab */}
        {activeTab === 'code' && (
          <div className="space-y-4">
            <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
              <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <Code size={16} className="text-blue-600" />
                Basic Cleaning Code
              </h4>
              <div className="bg-gray-900 text-gray-100 p-3 rounded text-sm font-mono overflow-x-auto">
                <pre>{cleaningCode}</pre>
              </div>
            </div>

            {comprehensiveCode && (
              <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <Code size={16} className="text-green-600" />
                  Comprehensive Cleaning Pipeline
                </h4>
                <div className="bg-gray-900 text-gray-100 p-3 rounded text-sm font-mono overflow-x-auto">
                  <pre>{comprehensiveCode}</pre>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Visualization Tab */}
        {activeTab === 'visualization' && (
          <div className="space-y-4">
            <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <BarChart2 size={16} className="text-purple-600" />
              Visualization Suggestions
            </h4>

            {visualizationSuggestions.length > 0 ? (
              <div className="space-y-3">
                {visualizationSuggestions.map((suggestion, index) => (
                  <div key={index} className="bg-gray-50 p-3 rounded-lg border border-gray-200">
                    <div className="flex items-start gap-3">
                      <div className="w-8 h-8 bg-purple-100 rounded flex items-center justify-center flex-shrink-0">
                        <BarChart2 size={16} className="text-purple-600" />
                      </div>
                      <div className="flex-1">
                        <h5 className="font-medium text-gray-900 mb-1">{suggestion.type.replace('_', ' ')}</h5>
                        <p className="text-sm text-gray-600 mb-2">{suggestion.description}</p>
                        {suggestion.recommended_code && (
                          <div className="bg-gray-100 p-2 rounded text-xs font-mono text-gray-700">
                            {suggestion.recommended_code}
                          </div>
                        )}
                        {suggestion.insight && (
                          <p className="text-xs text-gray-500 mt-1">{suggestion.insight}</p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-gray-50 p-4 rounded border border-gray-200 text-center">
                <p className="text-gray-600">No visualization suggestions available for this dataset.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
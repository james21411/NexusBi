import { useState } from 'react';
import { 
  BarChart, Bar, LineChart, Line, AreaChart, Area, ScatterChart, Scatter,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, 
  PieChart, Pie, Cell 
} from 'recharts';
import { 
  ChevronDown, ChevronRight, BarChart3, PieChart as PieChartIcon, 
  TrendingUp, Activity, Calculator, Database, AlertTriangle,
  CheckCircle, XCircle, Info, X
} from 'lucide-react';

// Types for our statistics
interface StatisticsData {
  numericData: Record<string, number[]>;
  categoricalData: Record<string, string[]>;
  correlations: Record<string, Record<string, number>>;
  missingValues: Record<string, { count: number; percentage: number }>;
  outliers: Record<string, { count: number; percentage: number; bounds: { lower: number; upper: number } }>;
  descriptiveStats: Record<string, {
    count: number;
    mean: number;
    std: number;
    min: number;
    q1: number;
    median: number;
    q3: number;
    max: number;
  }>;
  // Real data from API
  source_name?: string;
  total_rows?: number;
  columns?: Array<{ name: string; type: string }>;
  sample_data?: any[];
  type_distribution?: Record<string, number>;
  originalData?: any; // Store original API response
}

// Sample data for demonstration
const sampleStatisticsData: StatisticsData = {
  numericData: {
    'revenue': [12000, 15000, 18000, 16500, 21000, 19500, 24000, 22500, 20000, 23000],
    'sales': [4000, 3200, 5000, 4500, 6000, 5500, 7200, 6800, 5900, 6500],
    'costs': [2400, 2210, 2900, 2700, 3100, 2950, 3400, 3300, 3050, 3150]
  },
  categoricalData: {
    'department': ['Sales', 'Marketing', 'Support', 'R&D', 'Sales', 'Marketing', 'Support', 'R&D', 'Sales', 'Marketing'],
    'status': ['Active', 'Pending', 'Completed', 'Active', 'Completed', 'Active', 'Pending', 'Active', 'Completed', 'Active']
  },
  correlations: {
    'revenue': { sales: 0.92, costs: 0.75 },
    'sales': { revenue: 0.92, costs: 0.68 },
    'costs': { revenue: 0.75, sales: 0.68 }
  },
  missingValues: {
    'revenue': { count: 0, percentage: 0 },
    'sales': { count: 1, percentage: 10 },
    'department': { count: 2, percentage: 20 }
  },
  outliers: {
    'revenue': { count: 1, percentage: 10, bounds: { lower: 8000, upper: 28000 } },
    'sales': { count: 0, percentage: 0, bounds: { lower: 2000, upper: 8000 } }
  },
  descriptiveStats: {
    'revenue': {
      count: 10, mean: 19250, std: 4250, min: 12000, q1: 16500, 
      median: 19000, q3: 21750, max: 24000
    },
    'sales': {
      count: 10, mean: 5170, std: 1350, min: 3200, q1: 4500, 
      median: 5250, q3: 6000, max: 7200
    },
    'costs': {
      count: 10, mean: 2906, std: 420, min: 2210, q1: 2700, 
      median: 2950, q3: 3100, max: 3400
    }
  }
};

const COLORS = ['#007acc', '#FF6B00', '#00C49F', '#FFB800', '#9C27B0', '#F44336'];

interface CollapsibleSectionProps {
  title: string;
  icon: React.ReactNode;
  children: React.ReactNode;
  defaultExpanded?: boolean;
  badge?: string;
}

interface StatisticsViewProps {
  data?: StatisticsData; // Real data from API
  sourceName?: string;
  onClose?: () => void;
  loading?: boolean;
  error?: string;
}

function CollapsibleSection({ title, icon, children, defaultExpanded = false, badge }: CollapsibleSectionProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  return (
    <div className="bg-[#3e3e42] rounded border border-[#454545] mb-4">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-[#454545] transition-colors rounded-t"
      >
        <div className="flex items-center gap-3">
          <div className="text-[#007acc]">{icon}</div>
          <span className="text-gray-200 font-medium">{title}</span>
          {badge && (
            <span className="bg-[#007acc] text-white text-xs px-2 py-0.5 rounded-full">
              {badge}
            </span>
          )}
        </div>
        {isExpanded ? <ChevronDown size={16} className="text-gray-400" /> : <ChevronRight size={16} className="text-gray-400" />}
      </button>
      {isExpanded && (
        <div className="px-4 pb-4">
          {children}
        </div>
      )}
    </div>
  );
}

interface StatsCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: 'up' | 'down' | 'neutral';
  color?: string;
}

function StatsCard({ title, value, subtitle, trend, color = '#007acc' }: StatsCardProps) {
  const trendIcon = trend === 'up' ? '↗' : trend === 'down' ? '↘' : '→';
  const trendColor = trend === 'up' ? '#00C49F' : trend === 'down' ? '#FF6B00' : '#9CA3AF';

  return (
    <div className="bg-[#454545] p-3 rounded border border-[#555555]">
      <p className="text-gray-400 text-xs mb-1">{title}</p>
      <div className="flex items-center justify-between">
        <p className="text-white text-lg font-semibold" style={{ color }}>{value}</p>
        {trend && <span className="text-xs" style={{ color: trendColor }}>{trendIcon}</span>}
      </div>
      {subtitle && <p className="text-gray-500 text-xs mt-1">{subtitle}</p>}
    </div>
  );
}

export function StatisticsView({ data: realData, sourceName, onClose, loading = false, error }: StatisticsViewProps = {}) {
  const [activeTab, setActiveTab] = useState('overview');
  const data = realData || sampleStatisticsData;
  const actualSourceName = sourceName || realData?.source_name || 'Source de données';

  // R's summary() equivalent using pandas describe()
  const renderDescriptiveStatistics = () => (
    <div className="space-y-4">
      <div className="bg-[#454545] p-4 rounded border border-[#555555]">
        <h4 className="text-gray-200 font-medium mb-3 flex items-center gap-2">
          <Calculator size={16} className="text-[#007acc]" />
          Statistiques Descriptives (Équivalent R summary())
        </h4>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[#555555]">
                <th className="text-left text-gray-300 py-2">Variable</th>
                <th className="text-right text-gray-300 py-2">Count</th>
                <th className="text-right text-gray-300 py-2">Mean</th>
                <th className="text-right text-gray-300 py-2">Std</th>
                <th className="text-right text-gray-300 py-2">Min</th>
                <th className="text-right text-gray-300 py-2">Q1</th>
                <th className="text-right text-gray-300 py-2">Median</th>
                <th className="text-right text-gray-300 py-2">Q3</th>
                <th className="text-right text-gray-300 py-2">Max</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(data.descriptiveStats).map(([variable, stats]) => (
                <tr key={variable} className="border-b border-[#555555]">
                  <td className="text-gray-200 py-2 font-medium">{variable}</td>
                  <td className="text-gray-300 text-right py-2">{stats.count}</td>
                  <td className="text-gray-300 text-right py-2">{stats.mean.toLocaleString()}</td>
                  <td className="text-gray-300 text-right py-2">{stats.std.toLocaleString()}</td>
                  <td className="text-gray-300 text-right py-2">{stats.min.toLocaleString()}</td>
                  <td className="text-gray-300 text-right py-2">{stats.q1.toLocaleString()}</td>
                  <td className="text-[#00C49F] text-right py-2 font-medium">{stats.median.toLocaleString()}</td>
                  <td className="text-gray-300 text-right py-2">{stats.q3.toLocaleString()}</td>
                  <td className="text-gray-300 text-right py-2">{stats.max.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-gray-500 text-xs mt-2">
          * Cette table correspond à la fonction summary() de R et describe() de pandas
        </p>
      </div>
    </div>
  );

  const renderDataQuality = () => (
    <div className="space-y-4">
      {/* Missing Values */}
      <CollapsibleSection
        title="Valeurs Manquantes"
        icon={<AlertTriangle size={16} />}
        badge={Object.keys(data?.missingValues || {}).length.toString()}
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Object.entries(data?.missingValues || {}).map(([column, info]) => (
            <div key={column} className="bg-[#454545] p-3 rounded border border-[#555555]">
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-200 font-medium">{column}</span>
                {info.count === 0 ? (
                  <CheckCircle size={16} className="text-green-500" />
                ) : (
                  <XCircle size={16} className="text-red-500" />
                )}
              </div>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Count:</span>
                  <span className="text-gray-200">{info.count}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Percentage:</span>
                  <span className="text-gray-200">{info.percentage}%</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CollapsibleSection>

      {/* Outliers */}
      <CollapsibleSection
        title="Valeurs Aberrantes (Outliers)"
        icon={<Activity size={16} />}
        badge={Object.keys(data?.outliers || {}).length.toString()}
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Object.entries(data?.outliers || {}).map(([column, info]) => (
            <div key={column} className="bg-[#454545] p-3 rounded border border-[#555555]">
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-200 font-medium">{column}</span>
                <span className="text-[#FF6B00] text-sm">{info.count} outliers</span>
              </div>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Percentage:</span>
                  <span className="text-gray-200">{info.percentage}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Lower bound:</span>
                  <span className="text-gray-200">{info.bounds.lower}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Upper bound:</span>
                  <span className="text-gray-200">{info.bounds.upper}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CollapsibleSection>
    </div>
  );

  const renderDistributions = () => (
    <div className="space-y-4">
      {/* Histograms for numeric data */}
      <CollapsibleSection
        title="Distribution des Variables Numériques"
        icon={<BarChart3 size={16} />}
        defaultExpanded
      >
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {Object.entries(data?.numericData || {}).map(([variable, values]) => (
            <div key={variable} className="bg-[#454545] p-4 rounded border border-[#555555]">
              <h5 className="text-gray-200 font-medium mb-3">{variable}</h5>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={values.map((value, index) => ({ value, index }))}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#555555" />
                  <XAxis dataKey="index" stroke="#cccccc" fontSize={12} />
                  <YAxis stroke="#cccccc" fontSize={12} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#3e3e42', border: '1px solid #555555' }}
                    labelStyle={{ color: '#cccccc' }}
                  />
                  <Bar dataKey="value" fill="#007acc" radius={[2, 2, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ))}
        </div>
      </CollapsibleSection>

      {/* Categorical data distributions */}
      <CollapsibleSection
        title="Distribution des Variables Catégorielles"
        icon={<PieChartIcon size={16} />}
      >
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {Object.entries(data?.categoricalData || {}).map(([variable, values]) => {
            const valueCounts = values.reduce((acc, val) => {
              acc[val] = (acc[val] || 0) + 1;
              return acc;
            }, {} as Record<string, number>);

            const pieData = Object.entries(valueCounts).map(([name, value]) => ({ name, value }));

            return (
              <div key={variable} className="bg-[#454545] p-4 rounded border border-[#555555]">
                <h5 className="text-gray-200 font-medium mb-3">{variable}</h5>
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      outerRadius={70}
                      fill="#8884d8"
                      dataKey="value"
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    >
                      {pieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#3e3e42', border: '1px solid #555555' }}
                      labelStyle={{ color: '#cccccc' }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            );
          })}
        </div>
      </CollapsibleSection>
    </div>
  );

  const renderCorrelations = () => (
    <div className="space-y-4">
      <CollapsibleSection
        title="Matrice de Corrélation"
        icon={<TrendingUp size={16} />}
        defaultExpanded
      >
        <div className="bg-[#454545] p-4 rounded border border-[#555555]">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[#555555]">
                  <th className="text-left text-gray-300 py-2"></th>
                  {Object.keys(data?.correlations || {}).map(key => (
                    <th key={key} className="text-center text-gray-300 py-2">{key}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {Object.entries(data?.correlations || {}).map(([rowKey, row]) => (
                  <tr key={rowKey} className="border-b border-[#555555]">
                    <td className="text-gray-200 py-2 font-medium">{rowKey}</td>
                    {Object.keys(data?.correlations || {}).map(colKey => {
                      const value = row[colKey] || data.correlations[colKey]?.[rowKey] || 0;
                      const intensity = Math.abs(value);
                      const color = value > 0 ? `rgba(0, 196, 159, ${intensity})` : `rgba(255, 107, 0, ${intensity})`;
                      
                      return (
                        <td key={colKey} className="text-center py-2">
                          <div 
                            className="w-12 h-8 mx-auto rounded flex items-center justify-center text-white text-xs font-medium"
                            style={{ backgroundColor: color }}
                          >
                            {value.toFixed(2)}
                          </div>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="flex items-center gap-4 mt-4 text-xs text-gray-400">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-[#00C49F] rounded"></div>
              <span>Positive correlation</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-[#FF6B00] rounded"></div>
              <span>Negative correlation</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-gray-500 rounded"></div>
              <span>No correlation</span>
            </div>
          </div>
        </div>
      </CollapsibleSection>

      {/* Scatter plots for strong correlations */}
      <CollapsibleSection
        title="Graphiques de Dispersion (Relations Fortes)"
        icon={<Activity size={16} />}
      >
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {Object.entries(data.correlations).map(([var1, correlations]) => 
            Object.entries(correlations)
              .filter(([_, corr]) => Math.abs(corr) > 0.7)
              .map(([var2, corr]) => {
                // Generate scatter data
                const scatterData = data.numericData[var1]?.map((val1, i) => ({
                  x: val1,
                  y: data.numericData[var2]?.[i] || 0
                })) || [];

                return (
                  <div key={`${var1}-${var2}`} className="bg-[#454545] p-4 rounded border border-[#555555]">
                    <h5 className="text-gray-200 font-medium mb-2">
                      {var1} vs {var2} (r = {corr.toFixed(3)})
                    </h5>
                    <ResponsiveContainer width="100%" height={200}>
                      <ScatterChart data={scatterData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#555555" />
                        <XAxis 
                          dataKey="x" 
                          stroke="#cccccc" 
                          fontSize={12}
                          name={var1}
                        />
                        <YAxis 
                          dataKey="y" 
                          stroke="#cccccc" 
                          fontSize={12}
                          name={var2}
                        />
                        <Tooltip 
                          contentStyle={{ backgroundColor: '#3e3e42', border: '1px solid #555555' }}
                          labelStyle={{ color: '#cccccc' }}
                        />
                        <Scatter dataKey="y" fill="#007acc" />
                      </ScatterChart>
                    </ResponsiveContainer>
                  </div>
                );
              })
          )}
        </div>
      </CollapsibleSection>
    </div>
  );

  const renderOverview = () => {
    // Calculate real statistics from API data or use sample data
    const realNumericColumns = realData?.columns?.filter(col => 
      ['int64', 'float64', 'int32', 'float32', 'int', 'float', 'double', 'number'].some(type => 
        col.type?.toLowerCase().includes(type)
      )
    ).length || Object.keys(data?.numericData || {}).length;
    
    const realCategoricalColumns = realData?.columns?.filter(col => 
      ['object', 'string', 'varchar', 'text', 'char'].some(type => 
        col.type?.toLowerCase().includes(type)
      )
    ).length || Object.keys(data?.categoricalData || {}).length;
    
    const totalMissingValues = (realData as any)?.missing_values || Object.values(data?.missingValues || {}).reduce((sum, val) => sum + val.count, 0);
    const totalRows = realData?.total_rows || 0;
    const totalColumns = realData?.columns?.length || 0;
    
    return (
      <div className="space-y-6">
        {/* Key Statistics Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatsCard 
            title="Variables Numériques" 
            value={realNumericColumns}
            subtitle="colonnes quantitatives"
            trend="up"
            color="#007acc"
          />
          <StatsCard 
            title="Variables Catégorielles" 
            value={realCategoricalColumns}
            subtitle="colonnes qualitatives"
            trend="neutral"
            color="#FF6B00"
          />
          <StatsCard 
            title="Données Manquantes" 
            value={totalMissingValues}
            subtitle={totalRows > 0 ? `${((totalMissingValues / (totalRows * totalColumns)) * 100).toFixed(1)}%` : "total"}
            trend={totalMissingValues > 0 ? "down" : "neutral"}
            color="#F44336"
          />
          <StatsCard 
            title="Total Lignes" 
            value={totalRows.toLocaleString()}
            subtitle="enregistrements"
            trend="up"
            color="#00C49F"
          />
        </div>

      {/* Quick preview of descriptive statistics */}
      <div className="bg-[#454545] p-4 rounded border border-[#555555]">
        <h4 className="text-gray-200 font-medium mb-3 flex items-center gap-2">
          <Info size={16} className="text-[#007acc]" />
          Aperçu des Statistiques Descriptives
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {Object.entries(data?.descriptiveStats || {}).slice(0, 3).map(([variable, stats]) => (
            <div key={variable} className="bg-[#3e3e42] p-3 rounded border border-[#555555]">
              <h5 className="text-gray-200 font-medium mb-2">{variable}</h5>
              <div className="space-y-1 text-xs">
                <div className="flex justify-between">
                  <span className="text-gray-400">Moyenne:</span>
                  <span className="text-gray-200">{stats.mean.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Médiane:</span>
                  <span className="text-gray-200">{stats.median.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Écart-type:</span>
                  <span className="text-gray-200">{stats.std.toLocaleString()}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
    );
  }

  const tabs = [
    { id: 'overview', label: 'Vue d\'ensemble', icon: <Database size={16} /> },
    { id: 'descriptive', label: 'Statistiques Descriptives', icon: <Calculator size={16} /> },
    { id: 'quality', label: 'Qualité des Données', icon: <AlertTriangle size={16} /> },
    { id: 'distributions', label: 'Distributions', icon: <BarChart3 size={16} /> },
    { id: 'correlations', label: 'Corrélations', icon: <TrendingUp size={16} /> }
  ];

  return (
    <div className="flex-1 bg-[#2d2d30] overflow-hidden">
      {/* Header */}
      <div className="bg-[#3e3e42] border-b border-[#454545] px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-gray-200 text-xl font-medium mb-1">Statistiques Avancées</h1>
            <p className="text-gray-400 text-sm">{actualSourceName} • Analyses statistiques complètes</p>
          </div>
          {onClose && (
            <button
              onClick={onClose}
              className="w-8 h-8 flex items-center justify-center text-gray-400 hover:text-gray-200 hover:bg-[#454545] rounded transition-colors"
            >
              <X size={20} />
            </button>
          )}
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="bg-[#3e3e42] border-b border-[#454545] px-6">
        <nav className="flex space-x-0">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-[#007acc] text-[#007acc] bg-[#2d2d30]'
                  : 'border-transparent text-gray-400 hover:text-gray-200 hover:bg-[#454545]'
              }`}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#007acc]"></div>
            <span className="ml-3 text-gray-400">Calcul des statistiques...</span>
          </div>
        ) : error ? (
          <div className="text-center py-12">
            <AlertTriangle size={48} className="text-red-500 mx-auto mb-4" />
            <p className="text-red-400">{error}</p>
          </div>
        ) : (
          <>
            {activeTab === 'overview' && renderOverview()}
            {activeTab === 'descriptive' && renderDescriptiveStatistics()}
            {activeTab === 'quality' && renderDataQuality()}
            {activeTab === 'distributions' && renderDistributions()}
            {activeTab === 'correlations' && renderCorrelations()}
          </>
        )}
      </div>
    </div>
  );
}
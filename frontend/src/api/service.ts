import axios from 'axios';
import { API_BASE_URL } from './config';

interface AIQueryResponse {
  response: string;
  model_used: string;
  tokens_used: number;
  suggestions?: string[];
}

interface DataAnalysisResponse {
  analysis_results: any;
  cleaning_code: string;
  visualization_suggestions: any[];
  visualization_code?: string;
  extended_visualization_suggestions?: any[];
  recommendations: string[];
  comprehensive_cleaning_code?: string;
}

export interface DataSource {
  id: number;
  name: string;
  type: string;
  project_id: number;
  connection_string?: string;
  file_path?: string;
  schema_info?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface DataSourceCreate {
  name: string;
  type: string;
  project_id: number;
  connection_string?: string;
  file_path?: string;
}

export interface DataSourceUpdate {
  name?: string;
  type?: string;
  connection_string?: string;
  file_path?: string;
  is_active?: boolean;
}

export async function sendAIQuery(
  query: string,
  model: string,
  authToken: string | null,
  temperature: number,
  maxTokens: number
): Promise<{ data?: AIQueryResponse; error?: string }> {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/ai/query`,
      {
        query,
        model,
        temperature,
        max_tokens: maxTokens,
      },
      {
        headers: authToken ? { Authorization: `Bearer ${authToken}` } : {},
      }
    );
    return { data: response.data };
  } catch (error) {
    console.error('Error sending AI query:', error);
    if (axios.isAxiosError(error)) {
      return { error: error.response?.data?.detail || error.message };
    }
    return { error: 'Unknown error occurred' };
  }
}

export async function analyzeData(
  projectId: number,
  dataSourceId: number,
  analysisType: string = 'quality',
  treatmentStrategy: string = 'mean',
  authToken: string | null
): Promise<{ data?: DataAnalysisResponse; error?: string }> {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/ai/analyze-data`,
      {
        project_id: projectId,
        data_source_id: dataSourceId,
        analysis_type: analysisType,
        treatment_strategy: treatmentStrategy,
      },
      {
        headers: authToken ? { Authorization: `Bearer ${authToken}` } : {},
      }
    );
    return { data: response.data };
  } catch (error) {
    console.error('Error analyzing data:', error);
    if (axios.isAxiosError(error)) {
      return { error: error.response?.data?.detail || error.message };
    }
    return { error: 'Unknown error occurred' };
  }
}

export async function generateCleaningCode(
  projectId: number,
  dataSourceId: number,
  treatmentStrategy: string = 'mean',
  authToken: string | null
): Promise<{ data?: { cleaning_code: string; comprehensive_cleaning_code?: string; language: string; libraries: string[] }; error?: string }> {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/ai/generate-code`,
      {
        project_id: projectId,
        data_source_id: dataSourceId,
        treatment_strategy: treatmentStrategy,
      },
      {
        headers: authToken ? { Authorization: `Bearer ${authToken}` } : {},
      }
    );
    return { data: response.data };
  } catch (error) {
    console.error('Error generating cleaning code:', error);
    if (axios.isAxiosError(error)) {
      return { error: error.response?.data?.detail || error.message };
    }
    return { error: 'Unknown error occurred' };
  }
}

export async function getVisualizationSuggestions(
  projectId: number,
  dataSourceId: number,
  authToken: string | null
): Promise<{ data?: { visualization_suggestions: any[]; visualization_code?: string }; error?: string }> {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/ai/analyze-data`,
      {
        project_id: projectId,
        data_source_id: dataSourceId,
        analysis_type: 'visualization',
      },
      {
        headers: authToken ? { Authorization: `Bearer ${authToken}` } : {},
      }
    );
    return {
      data: {
        visualization_suggestions: response.data.visualization_suggestions,
        visualization_code: response.data.visualization_code
      }
    };
  } catch (error) {
    console.error('Error getting visualization suggestions:', error);
    if (axios.isAxiosError(error)) {
      return { error: error.response?.data?.detail || error.message };
    }
    return { error: 'Unknown error occurred' };
  }
}

// Data Sources API functions
export async function getDataSources(
  authToken: string | null = null
): Promise<{ data?: DataSource[]; error?: string }> {
  try {
    console.log('Fetching data sources from:', `${API_BASE_URL}/data-sources/`);
    
    const response = await axios.get(
      `${API_BASE_URL}/data-sources/`,
      {
        headers: authToken ? { Authorization: `Bearer ${authToken}` } : {},
        timeout: 30000
      }
    );
    
    console.log('Data sources response:', response.data);
    return { data: response.data };
  } catch (error) {
    console.error('Error fetching data sources:', error);
    if (axios.isAxiosError(error)) {
      return { error: error.response?.data?.detail || error.message };
    }
    return { error: 'Unknown error occurred' };
  }
}

export async function createDataSource(
  dataSource: DataSourceCreate,
  authToken: string | null = null
): Promise<{ data?: DataSource; error?: string }> {
  try {
    console.log('Creating data source:', dataSource);
    
    const response = await axios.post(
      `${API_BASE_URL}/data-sources/`,
      dataSource,
      {
        headers: authToken ? { Authorization: `Bearer ${authToken}` } : {},
        timeout: 10000
      }
    );
    
    console.log('Data source created:', response.data);
    return { data: response.data };
  } catch (error) {
    console.error('Error creating data source:', error);
    if (axios.isAxiosError(error)) {
      return { error: error.response?.data?.detail || error.message };
    }
    return { error: 'Unknown error occurred' };
  }
}

export async function updateDataSource(
  dataSourceId: number,
  updates: DataSourceUpdate,
  authToken: string | null
): Promise<{ data?: DataSource; error?: string }> {
  try {
    const response = await axios.put(
      `${API_BASE_URL}/data-sources/${dataSourceId}`,
      updates,
      {
        headers: authToken ? { Authorization: `Bearer ${authToken}` } : {},
      }
    );
    return { data: response.data };
  } catch (error) {
    console.error('Error updating data source:', error);
    if (axios.isAxiosError(error)) {
      return { error: error.response?.data?.detail || error.message };
    }
    return { error: 'Unknown error occurred' };
  }
}

export async function deleteDataSource(
  dataSourceId: number,
  authToken: string | null
): Promise<{ data?: any; error?: string }> {
  try {
    const response = await axios.delete(
      `${API_BASE_URL}/data-sources/${dataSourceId}`,
      {
        headers: authToken ? { Authorization: `Bearer ${authToken}` } : {},
      }
    );
    return { data: response.data };
  } catch (error) {
    console.error('Error deleting data source:', error);
    if (axios.isAxiosError(error)) {
      return { error: error.response?.data?.detail || error.message };
    }
    return { error: 'Unknown error occurred' };
  }
}

export async function syncDataSource(
  dataSourceId: number,
  authToken: string | null
): Promise<{ data?: any; error?: string }> {
  try {
    // Use demo endpoint if no auth token is available
    const endpoint = authToken
      ? `${API_BASE_URL}/data-sources/${dataSourceId}/sync`
      : `${API_BASE_URL}/data-sources/${dataSourceId}/sync-demo`;
    
    const response = await axios.post(
      endpoint,
      {},
      {
        headers: authToken ? { Authorization: `Bearer ${authToken}` } : {},
      }
    );
    return { data: response.data };
  } catch (error) {
    console.error('Error syncing data source:', error);
    if (axios.isAxiosError(error)) {
      return { error: error.response?.data?.detail || error.message };
    }
    return { error: 'Unknown error occurred' };
  }
}

// Add the missing auth functions that were imported
export async function loginUser(email: string, password: string) {
  try {
    const response = await axios.post(`${API_BASE_URL}/auth/login`, {
      email,
      password,
    });
    return { data: response.data };
  } catch (error) {
    console.error('Login error:', error);
    if (axios.isAxiosError(error)) {
      return { error: error.response?.data?.detail || error.message };
    }
    return { error: 'Login failed' };
  }
}

export async function registerUser(email: string, password: string, fullName: string) {
  try {
    const response = await axios.post(`${API_BASE_URL}/auth/register`, {
      email,
      password,
      full_name: fullName,
    });
    return { data: response.data };
  } catch (error) {
    console.error('Registration error:', error);
    if (axios.isAxiosError(error)) {
      return { error: error.response?.data?.detail || error.message };
    }
    return { error: 'Registration failed' };
  }
}

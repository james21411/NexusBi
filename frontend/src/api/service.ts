import { apiEndpoints, API_BASE_URL } from './config';

interface ApiResponse<T> {
  data?: T;
  error?: string;
  status?: number;
}

export async function fetchFromAPI<T>(
  endpoint: string,
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' = 'GET',
  data: any = null,
  authToken: string | null = null
): Promise<ApiResponse<T>> {
  try {
    // Get the full URL from the endpoint configuration
    // Use type assertion to handle the complex endpoint structure
    const endpointKey = endpoint as keyof typeof apiEndpoints;
    const endpointConfig = apiEndpoints[endpointKey];

    console.log('DEBUG: fetchFromAPI called with endpoint:', endpoint);
    console.log('DEBUG: endpointConfig:', endpointConfig);
    console.log('DEBUG: All available endpoints:', apiEndpoints);

    // Handle nested endpoint paths
    let url: string;

    // Try to navigate the endpoint structure
    if (endpoint.includes('.')) {
      const parts = endpoint.split('.');
      let current: any = apiEndpoints;

      // Navigate through each part of the endpoint path
      for (const part of parts) {
        if (current && current[part]) {
          current = current[part];
        } else {
          // If any part is not found, break and use fallback
          current = null;
          break;
        }
      }

      // If we successfully navigated to a string URL, use it
      if (typeof current === 'string') {
        url = current;
      } else {
        // Use fallback URL construction
        console.warn('DEBUG: Endpoint not found in config, using fallback');
        url = `${API_BASE_URL}/${endpoint.replace('.', '/')}`;
      }
    } else {
      // For simple endpoints without dots
      url = typeof endpointConfig === 'string' ? endpointConfig : `${API_BASE_URL}/${endpoint}`;
    }

    console.log('DEBUG: Final URL to be called:', url);

    const options: RequestInit = {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
    };

    // Add authorization header if token is provided
    if (authToken) {
      options.headers = {
        ...options.headers,
        'Authorization': `Bearer ${authToken}`,
      };
    }

    if (data && (method === 'POST' || method === 'PUT')) {
      options.body = JSON.stringify(data);
    }

    console.log('DEBUG: Fetching URL:', url);
    console.log('DEBUG: Fetch options:', options);

    const response = await fetch(url, options);

    console.log('DEBUG: Response status:', response.status);
    console.log('DEBUG: Response headers:', [...response.headers.entries()]);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error('DEBUG: API Error response:', errorData);
      return {
        error: errorData.detail || `HTTP error! status: ${response.status}`,
        status: response.status,
      };
    }

    const responseData = await response.json();
    return { data: responseData, status: response.status };

  } catch (error) {
    console.error('API Error:', error);
    return {
      error: error instanceof Error ? error.message : 'Unknown error occurred',
      status: 500,
    };
  }
}

// Auth API functions
export async function registerUser(email: string, password: string, fullName: string) {
  return fetchFromAPI('auth.register', 'POST', {
    email,
    password,
    full_name: fullName,
  });
}

export async function loginUser(email: string, password: string) {
  return fetchFromAPI('auth.login', 'POST', {
    username: email,
    password,
  });
}

// User API functions
export async function createAPIKey(keyName: string, keyType: string, apiKeyValue: string, authToken: string) {
  return fetchFromAPI('user.apiKeys.create', 'POST', {
    key_name: keyName,
    key_type: keyType,
    api_key_value: apiKeyValue,
  }, authToken);
}

export async function listAPIKeys(authToken: string) {
  return fetchFromAPI('user.apiKeys.list', 'GET', null, authToken);
}

// Chatbot API functions
export async function configureChatbot(
  selectedModel: string,
  temperature: number,
  maxTokens: number,
  language: string,
  authToken: string
) {
  return fetchFromAPI('user.chatbot.config', 'POST', {
    selected_model: selectedModel,
    temperature,
    max_tokens: maxTokens,
    language,
  }, authToken);
}

export async function sendChatbotQuery(query: string, authToken: string) {
  return fetchFromAPI('user.chatbot.query', 'POST', { query }, authToken);
}

export async function getChatbotModels(authToken: string) {
  return fetchFromAPI('user.chatbot.models', 'GET', null, authToken);
}

// Settings API functions
export async function getSystemSettings(authToken: string) {
  return fetchFromAPI('settings.system', 'GET', null, authToken);
}

export async function getAISettings(authToken: string) {
  return fetchFromAPI('settings.aiStatus', 'GET', null, authToken);
}

// AI Assistant API functions
export async function sendAIQuery(query: string, model: string, authToken: string | null, temperature: number = 0.7, maxTokens: number = 1024) {
  console.log('DEBUG: sendAIQuery called with:', {
    query,
    model,
    authToken: authToken ? 'token-present' : 'no-token',
    temperature,
    maxTokens
  });

  const result = await fetchFromAPI('ai.query', 'POST', {
    query,
    model,
    temperature,
    max_tokens: maxTokens,
  }, authToken);

  console.log('DEBUG: sendAIQuery result:', result);
  return result;
}

export async function getAISuggestions(context: string, authToken: string) {
  return fetchFromAPI('ai.suggestions', 'POST', {
    context,
  }, authToken);
}
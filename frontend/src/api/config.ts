export const API_BASE_URL = 'http://localhost:8000/api/v1';

export const apiEndpoints = {
  auth: {
    register: `${API_BASE_URL}/auth/register`,
    login: `${API_BASE_URL}/auth/login`,
  },
  user: {
    apiKeys: {
      create: `${API_BASE_URL}/user/api-keys/create`,
      list: `${API_BASE_URL}/user/api-keys/list`,
    },
    chatbot: {
      config: `${API_BASE_URL}/user/chatbot/config`,
      query: `${API_BASE_URL}/user/chatbot/query`,
      models: `${API_BASE_URL}/user/chatbot/models`,
    },
  },
  settings: {
    system: `${API_BASE_URL}/settings/system`,
    aiStatus: `${API_BASE_URL}/settings/ai/status`,
  },
  ai: {
    query: `${API_BASE_URL}/ai/query`,
    suggestions: `${API_BASE_URL}/ai/suggestions`,
    models: `${API_BASE_URL}/ai/models`,
    config: `${API_BASE_URL}/ai/config`,
  },
};
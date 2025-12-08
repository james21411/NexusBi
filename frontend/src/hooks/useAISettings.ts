import { useState, useEffect } from 'react';

interface AISettings {
  aiProvider: string;
  aiModel: string;
  apiKey: string;
  temperature: number;
  maxTokens: number;
  enableAutoSuggestions: boolean;
}

export function useAISettings() {
  const [settings, setSettings] = useState<AISettings>({
    aiProvider: 'gemini', // Use Gemini as default since it has backend fallback
    aiModel: 'gemini-pro',
    apiKey: '', // API key is now optional
    temperature: 0.7,
    maxTokens: 2000,
    enableAutoSuggestions: true,
  });

  useEffect(() => {
    // Charger les paramètres depuis localStorage au démarrage
    const savedSettings = localStorage.getItem('aiSettings');
    if (savedSettings) {
      try {
        const parsedSettings = JSON.parse(savedSettings);
        setSettings({
          aiProvider: parsedSettings.aiProvider || 'openai',
          aiModel: parsedSettings.aiModel || 'gpt-4',
          apiKey: parsedSettings.apiKey || '',
          temperature: parsedSettings.temperature || 0.7,
          maxTokens: parsedSettings.maxTokens || 2000,
          enableAutoSuggestions: parsedSettings.enableAutoSuggestions || true,
        });
      } catch (error) {
        console.error('Erreur de chargement des paramètres AI:', error);
      }
    }
  }, []);

  return settings;
}
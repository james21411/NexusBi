import { TopMenuBar } from './TopMenuBar';
import { Sidebar } from './Sidebar';
import { useState } from 'react';
import {
  Settings,
  Palette,
  Key,
  Brain,
  Database,
  Bell,
  Shield,
  Users,
  Globe,
  Download,
  Trash2,
  Save,
  Eye,
  EyeOff,
  Check
} from 'lucide-react';

interface SettingsViewProps {
  currentView?: string;
  onViewChange?: (view: string) => void;
  onShowImportModal?: () => void;
}

export function SettingsView({ currentView, onViewChange, onShowImportModal }: SettingsViewProps) {
  const [activeSection, setActiveSection] = useState('general');
  const [showApiKey, setShowApiKey] = useState(false);

  // Charger les paramètres depuis localStorage au démarrage
  const [settings, setSettings] = useState(() => {
    const savedSettings = localStorage.getItem('aiSettings');
    return savedSettings ? JSON.parse(savedSettings) : {
      // Général
      appName: 'NexusBi',
      language: 'fr',
      timezone: 'Europe/Paris',
      dateFormat: 'DD/MM/YYYY',

      // Thème
      theme: 'light',
      primaryColor: '#0056D2',
      accentColor: '#FF6B00',
      fontSize: 'medium',
      compactMode: false,

      // IA & Modèles
      aiProvider: 'openai',
      aiModel: 'gpt-4',
      apiKey: '',
      temperature: 0.7,
      maxTokens: 2000,
      enableAutoSuggestions: true,

      // Base de données
      dbType: 'postgresql',
      dbHost: 'localhost',
      dbPort: '5432',
      dbName: 'nexusbi',
      dbUser: 'admin',
      dbPassword: '',
      autoBackup: true,
      backupFrequency: 'daily',

      // Notifications
      emailNotifications: true,
      pushNotifications: false,
      notifyOnReportReady: true,
      notifyOnDataSync: true,
      notifyOnErrors: true,
      notifyWeeklySummary: true,

      // Sécurité
      twoFactorAuth: false,
      sessionTimeout: '30',
      passwordExpiry: '90',
      ipWhitelist: '',
      allowApiAccess: true,

      // Équipe
      defaultRole: 'viewer',
      allowInvites: true,
      maxUsers: '50',
      requireApproval: true,

      // Exportation
      defaultExportFormat: 'pdf',
      includeMetadata: true,
      compressExports: false,
      watermark: false,
    };
  });

  const sections = [
    { id: 'general', icon: Settings, label: 'Général' },
    { id: 'theme', icon: Palette, label: 'Apparence' },
    { id: 'ai', icon: Brain, label: 'IA & Modèles' },
    { id: 'database', icon: Database, label: 'Base de données' },
    { id: 'notifications', icon: Bell, label: 'Notifications' },
    { id: 'security', icon: Shield, label: 'Sécurité' },
    { id: 'team', icon: Users, label: 'Équipe' },
    { id: 'export', icon: Download, label: 'Exportation' },
    { id: 'advanced', icon: Globe, label: 'Avancé' },
  ];

  const handleChange = (key: string, value: any) => {
    setSettings({ ...settings, [key]: value });
  };

  const handleSave = () => {
    console.log('Paramètres sauvegardés:', settings);
    // Sauvegarder dans localStorage
    localStorage.setItem('aiSettings', JSON.stringify(settings));
    // Afficher notification de succès
    alert('Paramètres sauvegardés avec succès !');
  };

  return (
    <div className="flex flex-col h-screen">
      <TopMenuBar
        currentView={currentView}
        onViewChange={onViewChange}
        onShowImportModal={onShowImportModal}
      />

      <div className="flex flex-1 overflow-hidden bg-gray-50">
        <Sidebar activeView="settings" onNavigate={onViewChange} />

        <div className="flex flex-1 overflow-hidden">
          {/* Menu latéral des sections */}
          <div className="w-64 bg-white border-r border-gray-200 overflow-y-auto">
            <div className="p-6">
              <h2 className="text-gray-800 mb-1">Paramètres</h2>
              <p className="text-gray-600">Configurez votre application</p>
            </div>

            <nav className="px-3 pb-6">
              {sections.map((section) => {
                const Icon = section.icon;
                return (
                  <button
                    key={section.id}
                    onClick={() => setActiveSection(section.id)}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg mb-1 transition-colors ${
                      activeSection === section.id
                        ? 'bg-[#0056D2] text-white'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <Icon size={20} />
                    <span>{section.label}</span>
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Contenu des paramètres */}
          <div className="flex-1 overflow-y-auto">
            <div className="max-w-4xl mx-auto p-8">
              {/* GÉNÉRAL */}
              {activeSection === 'general' && (
                <div>
                  <div className="mb-8">
                    <h1 className="text-gray-800 mb-2">Paramètres Généraux</h1>
                    <p className="text-gray-600">Configuration de base de l'application</p>
                  </div>

                  <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-6">
                    <div>
                      <label className="block text-gray-700 mb-2">Nom de l'application</label>
                      <input
                        type="text"
                        value={settings.appName}
                        onChange={(e) => handleChange('appName', e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0056D2]"
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-gray-700 mb-2">Langue</label>
                        <select
                          value={settings.language}
                          onChange={(e) => handleChange('language', e.target.value)}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0056D2]"
                        >
                          <option value="fr">Français</option>
                          <option value="en">English</option>
                          <option value="es">Español</option>
                          <option value="de">Deutsch</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-gray-700 mb-2">Fuseau horaire</label>
                        <select
                          value={settings.timezone}
                          onChange={(e) => handleChange('timezone', e.target.value)}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0056D2]"
                        >
                          <option value="Europe/Paris">Europe/Paris (GMT+1)</option>
                          <option value="Europe/London">Europe/London (GMT+0)</option>
                          <option value="America/New_York">America/New York (GMT-5)</option>
                          <option value="Asia/Tokyo">Asia/Tokyo (GMT+9)</option>
                        </select>
                      </div>
                    </div>

                    <div>
                      <label className="block text-gray-700 mb-2">Format de date</label>
                      <select
                        value={settings.dateFormat}
                        onChange={(e) => handleChange('dateFormat', e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0056D2]"
                      >
                        <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                        <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                        <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                      </select>
                    </div>
                  </div>
                </div>
              )}

              {/* APPARENCE */}
              {activeSection === 'theme' && (
                <div>
                  <div className="mb-8">
                    <h1 className="text-gray-800 mb-2">Apparence</h1>
                    <p className="text-gray-600">Personnalisez l'interface de l'application</p>
                  </div>

                  <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-6">
                    <div>
                      <label className="block text-gray-700 mb-2">Thème</label>
                      <div className="grid grid-cols-3 gap-4">
                        <button
                          onClick={() => handleChange('theme', 'light')}
                          className={`p-4 border-2 rounded-lg transition-all ${
                            settings.theme === 'light'
                              ? 'border-[#0056D2] bg-blue-50'
                              : 'border-gray-300 hover:border-gray-400'
                          }`}
                        >
                          <div className="w-full h-20 bg-white rounded mb-2 border border-gray-200"></div>
                          <p className="text-gray-800">Clair</p>
                        </button>

                        <button
                          onClick={() => handleChange('theme', 'dark')}
                          className={`p-4 border-2 rounded-lg transition-all ${
                            settings.theme === 'dark'
                              ? 'border-[#0056D2] bg-blue-50'
                              : 'border-gray-300 hover:border-gray-400'
                          }`}
                        >
                          <div className="w-full h-20 bg-gray-900 rounded mb-2"></div>
                          <p className="text-gray-800">Sombre</p>
                        </button>

                        <button
                          onClick={() => handleChange('theme', 'auto')}
                          className={`p-4 border-2 rounded-lg transition-all ${
                            settings.theme === 'auto'
                              ? 'border-[#0056D2] bg-blue-50'
                              : 'border-gray-300 hover:border-gray-400'
                          }`}
                        >
                          <div className="w-full h-20 bg-gradient-to-r from-white to-gray-900 rounded mb-2"></div>
                          <p className="text-gray-800">Auto</p>
                        </button>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-gray-700 mb-2">Couleur principale</label>
                        <div className="flex gap-2">
                          <input
                            type="color"
                            value={settings.primaryColor}
                            onChange={(e) => handleChange('primaryColor', e.target.value)}
                            className="w-20 h-10 rounded border border-gray-300 cursor-pointer"
                          />
                          <input
                            type="text"
                            value={settings.primaryColor}
                            onChange={(e) => handleChange('primaryColor', e.target.value)}
                            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0056D2]"
                          />
                        </div>
                      </div>

                      <div>
                        <label className="block text-gray-700 mb-2">Couleur d'accent</label>
                        <div className="flex gap-2">
                          <input
                            type="color"
                            value={settings.accentColor}
                            onChange={(e) => handleChange('accentColor', e.target.value)}
                            className="w-20 h-10 rounded border border-gray-300 cursor-pointer"
                          />
                          <input
                            type="text"
                            value={settings.accentColor}
                            onChange={(e) => handleChange('accentColor', e.target.value)}
                            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0056D2]"
                          />
                        </div>
                      </div>
                    </div>

                    <div>
                      <label className="block text-gray-700 mb-2">Taille de police</label>
                      <select
                        value={settings.fontSize}
                        onChange={(e) => handleChange('fontSize', e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0056D2]"
                      >
                        <option value="small">Petite</option>
                        <option value="medium">Moyenne</option>
                        <option value="large">Grande</option>
                      </select>
                    </div>

                    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <div>
                        <p className="text-gray-800">Mode compact</p>
                        <p className="text-gray-600">Réduire l'espacement pour afficher plus de contenu</p>
                      </div>
                      <button
                        onClick={() => handleChange('compactMode', !settings.compactMode)}
                        className={`w-12 h-6 rounded-full transition-colors ${
                          settings.compactMode ? 'bg-[#0056D2]' : 'bg-gray-300'
                        }`}
                      >
                        <div className={`w-5 h-5 bg-white rounded-full transition-transform ${
                          settings.compactMode ? 'translate-x-6' : 'translate-x-0.5'
                        }`}></div>
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* IA & MODÈLES */}
              {activeSection === 'ai' && (
                <div>
                  <div className="mb-8">
                    <h1 className="text-gray-800 mb-2">IA & Modèles</h1>
                    <p className="text-gray-600">Configuration des services d'intelligence artificielle</p>
                  </div>

                  <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-8">
                    <div>
                      <h2 className="text-gray-800 mb-4">Fournisseur d'IA</h2>
                      <div className="grid grid-cols-2 gap-4">
                        <button
                          onClick={() => handleChange('aiProvider', 'openai')}
                          className={`p-4 border-2 rounded-lg transition-all ${
                            settings.aiProvider === 'openai'
                              ? 'border-[#0056D2] bg-blue-50'
                              : 'border-gray-300 hover:border-gray-400'
                          }`}
                        >
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 bg-black rounded flex items-center justify-center">
                              <span className="text-white font-bold text-sm">O</span>
                            </div>
                            <div className="text-left">
                              <p className="text-gray-800 font-medium">OpenAI</p>
                              <p className="text-gray-600 text-sm">GPT-4, DALL·E, Whisper</p>
                            </div>
                          </div>
                        </button>

                        <button
                          onClick={() => handleChange('aiProvider', 'gemini')}
                          className={`p-4 border-2 rounded-lg transition-all ${
                            settings.aiProvider === 'gemini'
                              ? 'border-[#0056D2] bg-blue-50'
                              : 'border-gray-300 hover:border-gray-400'
                          }`}
                        >
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded flex items-center justify-center">
                              <span className="text-white font-bold text-sm">G</span>
                            </div>
                            <div className="text-left">
                              <p className="text-gray-800 font-medium">Gemini</p>
                              <p className="text-gray-600 text-sm">Google AI, modèles multimodaux</p>
                            </div>
                          </div>
                        </button>
                      </div>
                    </div>

                    <div>
                      <h2 className="text-gray-800 mb-4">Modèle par défaut</h2>
                      <select
                        value={settings.aiModel}
                        onChange={(e) => handleChange('aiModel', e.target.value)}
                        className="w-full max-w-md px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0056D2]"
                      >
                        {settings.aiProvider === 'openai' ? (
                          <>
                            <option value="gpt-4">GPT-4 (Plus puissant)</option>
                            <option value="gpt-3.5-turbo">GPT-3.5 Turbo (Rapide)</option>
                            <option value="gpt-4o">GPT-4o (Optimisé)</option>
                            <option value="dall-e-3">DALL·E 3 (Images)</option>
                          </>
                        ) : (
                          <>
                            <option value="gemini-pro">Gemini Pro (Polyvalent)</option>
                            <option value="gemini-ultra">Gemini Ultra (Haute performance)</option>
                            <option value="gemini-flash">Gemini Flash (Rapide)</option>
                          </>
                        )}
                      </select>
                    </div>

                    <div>
                      <h2 className="text-gray-800 mb-4">Clé API</h2>
                      <div className="space-y-3">
                        <div className="flex gap-2">
                          <input
                            type={showApiKey ? 'text' : 'password'}
                            value={settings.apiKey}
                            onChange={(e) => handleChange('apiKey', e.target.value)}
                            placeholder="Entrez votre clé API"
                            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0056D2]"
                          />
                          <button
                            onClick={() => setShowApiKey(!showApiKey)}
                            className="px-4 py-2 bg-gray-100 border border-gray-300 rounded-lg hover:bg-gray-200 transition-colors"
                          >
                            {showApiKey ? <EyeOff size={20} /> : <Eye size={20} />}
                          </button>
                        </div>
                        <p className="text-gray-600 text-sm">
                          Votre clé API est stockée localement et n'est jamais envoyée à nos serveurs.
                        </p>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-6">
                      <div>
                        <label className="block text-gray-700 mb-2">Température</label>
                        <div className="flex items-center gap-3">
                          <input
                            type="range"
                            min="0"
                            max="1"
                            step="0.1"
                            value={settings.temperature}
                            onChange={(e) => handleChange('temperature', parseFloat(e.target.value))}
                            className="flex-1"
                          />
                          <span className="text-gray-800">{settings.temperature}</span>
                        </div>
                        <p className="text-gray-600 text-sm mt-1">
                          Contrôle la créativité (0 = précis, 1 = créatif)
                        </p>
                      </div>

                      <div>
                        <label className="block text-gray-700 mb-2">Tokens maximum</label>
                        <select
                          value={settings.maxTokens}
                          onChange={(e) => handleChange('maxTokens', parseInt(e.target.value))}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0056D2]"
                        >
                          <option value="1000">1000 tokens</option>
                          <option value="2000">2000 tokens</option>
                          <option value="4000">4000 tokens</option>
                          <option value="8000">8000 tokens</option>
                          <option value="16000">16000 tokens</option>
                        </select>
                        <p className="text-gray-600 text-sm mt-1">
                          Limite la longueur des réponses
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <div>
                        <p className="text-gray-800">Suggestions automatiques</p>
                        <p className="text-gray-600">Activer les suggestions de texte intelligentes</p>
                      </div>
                      <button
                        onClick={() => handleChange('enableAutoSuggestions', !settings.enableAutoSuggestions)}
                        className={`w-12 h-6 rounded-full transition-colors ${
                          settings.enableAutoSuggestions ? 'bg-[#0056D2]' : 'bg-gray-300'
                        }`}
                      >
                        <div className={`w-5 h-5 bg-white rounded-full transition-transform ${
                          settings.enableAutoSuggestions ? 'translate-x-6' : 'translate-x-0.5'
                        }`}></div>
                      </button>
                    </div>

                    <div className="bg-gray-50 rounded-lg p-4">
                      <h3 className="text-gray-800 mb-3">Test de connexion</h3>
                      <p className="text-gray-600 mb-4">
                        Vérifiez que votre clé API fonctionne correctement.
                      </p>
                      <button
                        onClick={() => console.log('Test de connexion API')}
                        className="px-6 py-2 bg-[#0056D2] text-white rounded-lg hover:bg-[#0045B0] transition-colors"
                      >
                        Tester la connexion
                      </button>
                    </div>

                  </div>
                </div>
              )}

              {/* Placeholder pour les autres sections */}
              {activeSection !== 'general' && activeSection !== 'theme' && activeSection !== 'ai' && (
                <div>
                  <div className="mb-8">
                    <h1 className="text-gray-800 mb-2">Section {activeSection}</h1>
                    <p className="text-gray-600">Cette section est en cours de développement</p>
                  </div>

                  <div className="bg-white rounded-lg border border-gray-200 p-6">
                    <p className="text-gray-600">Contenu à venir...</p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Bouton d'enregistrement - toujours visible */}
          <div className="sticky bottom-0 bg-white border-t border-gray-200 p-4">
            <div className="max-w-4xl mx-auto flex justify-end">
              <button
                onClick={handleSave}
                className="px-8 py-3 bg-[#0056D2] text-white rounded-lg hover:bg-[#0045B0] transition-colors flex items-center gap-2"
              >
                <Save size={18} />
                Enregistrer les paramètres
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
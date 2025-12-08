import { Send, Sparkles, Settings } from 'lucide-react';
import { useState, useEffect } from 'react';
import { useAISettings } from '../hooks/useAISettings';

const initialMessages = [
  {
    id: 1,
    type: 'ai' as const,
    text: 'Bonjour ! Je suis Nexus Assistant. Comment puis-je vous aider avec vos données aujourd\'hui ?',
  },
  {
    id: 2,
    type: 'user' as const,
    text: 'Peux-tu analyser les tendances du dernier trimestre ?',
  },
  {
    id: 3,
    type: 'ai' as const,
    text: 'Bien sûr ! J\'ai analysé vos données du dernier trimestre. J\'ai détecté une croissance de 23% en moyenne, avec un pic en mai. Souhaitez-vous un rapport détaillé ?',
  },
];

export function AIAssistant() {
  const [messages] = useState(initialMessages);
  const [inputValue, setInputValue] = useState('');
  const aiSettings = useAISettings();


  return (
    <div className="w-80 bg-gray-50 border-l border-gray-200 flex flex-col">
      {/* En-tête */}
      <div className="bg-white px-4 py-3 border-b border-gray-200 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 bg-[#FF6B00] rounded flex items-center justify-center">
            <Sparkles size={14} className="text-white" />
          </div>
          <div>
            <h2 className="text-gray-800 text-sm">Nexus Assistant</h2>
            <p className="text-xs text-gray-500">
              {aiSettings.aiProvider} • {aiSettings.aiModel}
              {aiSettings.apiKey ? ' ✓' : ' ⚠'}
            </p>
          </div>
        </div>
        <button
          onClick={() => {
            // Naviguer vers les paramètres AI
            window.location.hash = '#settings/ai';
            window.dispatchEvent(new Event('hashchange'));
          }}
          className="p-1 hover:bg-gray-100 rounded"
          title="Paramètres AI"
        >
          <Settings size={16} className="text-gray-600" />
        </button>
      </div>

      {/* Zone de conversation */}
      <div className="flex-1 overflow-auto p-4 space-y-3">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[85%] px-3 py-2 rounded text-sm ${
                message.type === 'user'
                  ? 'bg-[#0056D2] text-white rounded-br-none'
                  : 'bg-white border border-[#FF6B00] text-gray-800 rounded-bl-none'
              }`}
            >
              {message.text}
            </div>
          </div>
        ))}
      </div>

      {/* Zone de saisie */}
      <div className="bg-white px-4 py-3 border-t border-gray-200">
        <div className="flex gap-1.5">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Posez une question..."
            className="flex-1 px-3 py-1.5 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-[#FF6B00] focus:border-transparent text-sm"
          />
          <button className="w-8 h-8 bg-[#FF6B00] text-white rounded flex items-center justify-center hover:bg-[#e56100] transition-colors">
            <Send size={14} />
          </button>
        </div>
      </div>
    </div>
  );
}

import { Send, Sparkles } from 'lucide-react';
import { useState } from 'react';

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

  return (
    <div className="w-96 bg-gray-50 border-l border-gray-200 flex flex-col">
      {/* En-tête */}
      <div className="bg-white px-6 py-5 border-b border-gray-200 flex items-center gap-3">
        <div className="w-8 h-8 bg-[#FF6B00] rounded-lg flex items-center justify-center">
          <Sparkles size={18} className="text-white" />
        </div>
        <h2 className="text-gray-800">Nexus Assistant</h2>
      </div>

      {/* Zone de conversation */}
      <div className="flex-1 overflow-auto p-6 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] px-4 py-3 rounded-lg ${
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
      <div className="bg-white px-6 py-4 border-t border-gray-200">
        <div className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Posez une question..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#FF6B00] focus:border-transparent"
          />
          <button className="w-10 h-10 bg-[#FF6B00] text-white rounded-lg flex items-center justify-center hover:bg-[#e56100] transition-colors">
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}

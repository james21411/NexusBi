import { useState, useEffect } from 'react';
import { X, MessageSquare, Sparkles } from 'lucide-react';
import { sendAIQuery } from '../api/service';
import { useAISettings } from '../hooks/useAISettings';
import { useAuthContext } from '../api/authContext';

interface Message {
  id: number;
  type: 'user' | 'ai';
  text: string;
  modelUsed?: string;
  tokensUsed?: number;
}

interface UnifiedChatbotPanelProps {
  type: 'ai' | 'cleaning';
  initialMessages?: Message[];
  onClose?: () => void;
}

interface AIResponse {
  response: string;
  model_used: string;
  tokens_used: number;
  suggestions?: string[];
}

export function UnifiedChatbotPanel({
  type,
  initialMessages = [],
  onClose
}: UnifiedChatbotPanelProps) {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [inputValue, setInputValue] = useState('');
  const [isVisible, setIsVisible] = useState(true);
  const [panelWidth, setPanelWidth] = useState(380); // Default width in pixels
  const [isLoading, setIsLoading] = useState(false);
  const aiSettings = useAISettings();
  const { token: authToken } = useAuthContext();

  // Load initial messages from localStorage if available
  useEffect(() => {
    const savedMessages = localStorage.getItem('chatbotMessages');
    if (savedMessages) {
      try {
        const parsedMessages = JSON.parse(savedMessages);
        if (Array.isArray(parsedMessages)) {
          setMessages(parsedMessages);
        }
      } catch (error) {
        console.error('Error loading saved messages:', error);
      }
    }
  }, []);

  const toggleVisibility = () => {
    setIsVisible(!isVisible);
    if (onClose && !isVisible) {
      onClose();
    }
  };

  const handleSend = async () => {
    if (inputValue.trim()) {
      const newUserMessage: Message = {
        id: messages.length + 1,
        type: 'user',
        text: inputValue
      };

      setMessages([...messages, newUserMessage]);
      setInputValue('');
      setIsLoading(true);

      try {
        // Send query to backend API with AI settings
        // Allow communication without user account when API key is configured
        // if (!authToken) {
        //   throw new Error('No authentication token available. Please login first.');
        // }

        // Send query to backend - allow communication without user account
        try {
          console.log('DEBUG: Sending AI query with:', {
            query: inputValue,
            model: aiSettings.aiModel,
            authToken: authToken || null,
            temperature: aiSettings.temperature,
            maxTokens: aiSettings.maxTokens
          });

          const response = await sendAIQuery(
            inputValue,
            aiSettings.aiModel,
            authToken || null, // Allow null auth token
            aiSettings.temperature,
            aiSettings.maxTokens
          );

          console.log('DEBUG: AI query response received:', response);

        if (response.data) {
          // Type assertion for the response data
          const responseData = response.data as AIResponse;
          const aiResponse: Message = {
            id: messages.length + 2,
            type: 'ai',
            text: responseData.response || 'Réponse du modèle AI',
            modelUsed: responseData.model_used || aiSettings.aiModel,
            tokensUsed: responseData.tokens_used || 0
          };
          setMessages(prev => [...prev, aiResponse]);

          // Save messages to localStorage
          const updatedMessages = [...messages, newUserMessage, aiResponse];
          localStorage.setItem('chatbotMessages', JSON.stringify(updatedMessages));
        } else {
          const errorResponse: Message = {
            id: messages.length + 2,
            type: 'ai',
            text: `Erreur: ${response.error || 'Impossible de contacter le service AI'}`,
          };
          setMessages(prev => [...prev, errorResponse]);
        }
      } catch (error) {
        console.error('Error sending AI query:', error);
        let errorMessage = 'Erreur inconnue';

        if (error instanceof Error) {
          errorMessage = error.message;
          // Provide more specific error messages
          if (error.message.includes('404')) {
            errorMessage = 'Backend non disponible. Vérifiez que le serveur backend est démarré (http://127.0.0.1:8000)';
          } else if (error.message.includes('NetworkError')) {
            errorMessage = 'Impossible de se connecter au backend. Vérifiez la connexion réseau.';
          } else if (error.message.includes('CORS')) {
            errorMessage = 'Problème de configuration CORS. Le backend doit autoriser les requêtes depuis cette origine.';
          }
        }

        const errorResponse: Message = {
          id: messages.length + 2,
          type: 'ai',
          text: `⚠️ Erreur: ${errorMessage}`,
        };
        setMessages(prev => [...prev, errorResponse]);
      }
      } catch (error) {
        console.error('Error sending AI query:', error);
        const errorResponse: Message = {
          id: messages.length + 2,
          type: 'ai',
          text: `Erreur: ${error instanceof Error ? error.message : 'Erreur inconnue'}`,
        };
        setMessages(prev => [...prev, errorResponse]);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSend();
    }
  };

  // Resize handler
  const startResizing = (e: React.MouseEvent) => {
    e.preventDefault();
    const startX = e.clientX;
    const startWidth = panelWidth;

    const handleMouseMove = (e: MouseEvent) => {
      // Calculate new width (min 240px, max 50% of screen width)
      const newWidth = Math.max(240, Math.min(window.innerWidth * 0.5, startWidth + (e.clientX - startX)));
      setPanelWidth(newWidth);
    };

    const handleMouseUp = () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);
  };

  if (!isVisible) {
    return (
      <button
        onClick={toggleVisibility}
        className="fixed right-4 top-1/2 transform -translate-y-1/2 w-10 h-10 bg-blue-600 text-white rounded-l-lg flex items-center justify-center hover:bg-blue-700 transition-colors shadow-lg z-40"
        title={type === 'ai' ? "Ouvrir l'assistant IA" : "Ouvrir l'assistant de nettoyage"}
      >
        <MessageSquare size={20} />
      </button>
    );
  }

  return (
    <div
      className="relative bg-gray-50 border-l border-gray-200 flex flex-col h-full transition-all duration-200"
      style={{ width: `${panelWidth}px` }}
    >
      {/* Header with close button and resize handle */}
      <div className="bg-white px-5 py-4 border-b border-gray-200 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-[#FF6B00] rounded flex items-center justify-center">
            <Sparkles size={18} className="text-white" />
          </div>
          <div>
            <h2 className="text-gray-800 text-base font-medium">
              {type === 'ai' ? 'Nexus Assistant' : 'Assistant Nettoyage'}
            </h2>
            {type === 'ai' && (
              <p className="text-xs text-gray-500">
                {aiSettings.aiProvider} • {aiSettings.aiModel}
                {isLoading ? ' (traitement...)' : ' • Fonctionne sans compte'}
              </p>
            )}
          </div>
        </div>
        <button
          onClick={toggleVisibility}
          className="w-6 h-6 bg-gray-200 text-gray-600 rounded flex items-center justify-center hover:bg-gray-300 transition-colors"
          title="Fermer"
        >
          <X size={18} />
        </button>
      </div>

      {/* Resize handle (left side) */}
      <div
        className="absolute left-0 top-0 bottom-0 w-1 cursor-col-resize hover:bg-blue-500 hover:bg-opacity-20 transition-colors"
        onMouseDown={startResizing}
      />

      {/* Conversation area - full height with scrolling */}
      <div className="flex-1 overflow-auto p-5 space-y-4">
        {messages.length === 0 ? (
          <div className="flex justify-start">
            <div className="max-w-[90%] px-5 py-4 rounded-lg bg-white border border-[#FF6B00] text-gray-800 rounded-bl-none text-base">
              {type === 'ai'
                ? 'Bonjour ! Je suis Nexus Assistant. Comment puis-je vous aider avec vos données aujourd\'hui ?'
                : 'Je suis prêt à analyser et nettoyer vos données. Quelles actions souhaitez-vous entreprendre ?'}
            </div>
          </div>
        ) : (
          messages.map((message: Message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[90%] px-5 py-4 rounded-lg text-base ${
                  message.type === 'user'
                    ? 'bg-[#0056D2] text-white rounded-br-none'
                    : 'bg-white border border-[#FF6B00] text-gray-800 rounded-bl-none'
                }`}
              >
                {message.text}
                {message.type === 'ai' && message.modelUsed && (
                  <div className="mt-2 text-xs text-gray-500 flex justify-between items-center">
                    <span>Modèle: {message.modelUsed}</span>
                    {message.tokensUsed && <span>{message.tokensUsed} tokens</span>}
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Input area */}
      <div className="bg-white px-5 py-4 border-t border-gray-200">
        <div className="flex gap-1.5">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={type === 'ai' ? "Posez une question..." : "Décrivez le nettoyage nécessaire..."}
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#FF6B00] focus:border-transparent text-base"
          />
          <button
            onClick={handleSend}
            className="w-10 h-10 bg-[#FF6B00] text-white rounded-lg flex items-center justify-center hover:bg-[#e56100] transition-colors"
          >
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}

// Import Send icon
import { Send } from 'lucide-react';
import React, { useState } from 'react';
import Chatbot from 'react-chatbot-kit';
import config from './config';
import ActionProvider from './ActionProvider';
import MessageParser from './MessageParser';
import { FiSettings, FiClock, FiDownload, FiMinimize2, FiPlus } from 'react-icons/fi';
import nexusBiIcon from './NexusBi.png';

import 'react-chatbot-kit/build/main.css';
import './ChatBox.css';
import './NexusOptions.css';

const ChatBox = ({ sessionId, onSessionStart, onToggle }) => {
  const [showSettings, setShowSettings] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [showExport, setShowExport] = useState(false);
  const [darkMode, setDarkMode] = useState(false);

  const handleSettingsClick = () => {
    setShowSettings(!showSettings);
    setShowHistory(false);
    setShowExport(false);
  };

  const handleHistoryClick = () => {
    setShowHistory(!showHistory);
    setShowSettings(false);
    setShowExport(false);
  };

  const handleExportClick = () => {
    setShowExport(!showExport);
    setShowSettings(false);
    setShowHistory(false);
  };

  const handleNewChatClick = () => {
    // TODO: Implement new chat functionality
    console.log('New chat clicked');
    // This could reset the chat state, clear messages, etc.
  };

  const handleCloseClick = (onToggle) => {
    // Close all dropdowns and close the chatbot sidebar
    setShowSettings(false);
    setShowHistory(false);
    setShowExport(false);
    // Close the entire chatbot
    if (onToggle) {
      onToggle();
    }
    console.log('Close clicked');
  };

  return (
    <div className={`chatbox ${darkMode ? 'dark-mode' : ''}`} style={{ height: '100%', width: '100%', display: 'flex', flexDirection: 'column' }}>
      <div className="chatbox-header" style={{ flexShrink: 0, padding: '16px', position: 'relative' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <img src={nexusBiIcon} alt="NexusBI" style={{ width: '32px', height: '32px', borderRadius: '6px' }} />
            <h2 style={{ margin: '0 0 4px 0', fontSize: '18px', fontWeight: '600', color: 'white' }}>NexusBI Assistant</h2>
          </div>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', justifyContent: 'flex-end' }}>
            <button
              onClick={handleNewChatClick}
              style={{
                background: 'rgba(255, 255, 255, 0.1)',
                border: '1px solid rgba(255, 255, 255, 0.3)',
                color: 'white',
                cursor: 'pointer',
                padding: '6px',
                borderRadius: '6px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: 'all 0.2s',
                fontSize: '14px',
                minWidth: '32px',
                minHeight: '32px'
              }}
              title="Nouveau chat"
            >
              <FiPlus size={14} />
            </button>
            <button
              onClick={handleHistoryClick}
              style={{
                background: 'rgba(255, 255, 255, 0.1)',
                border: '1px solid rgba(255, 255, 255, 0.3)',
                color: 'white',
                cursor: 'pointer',
                padding: '6px',
                borderRadius: '6px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: 'all 0.2s',
                fontSize: '14px',
                minWidth: '32px',
                minHeight: '32px'
              }}
              title="Historique"
            >
              <FiClock size={14} />
            </button>
            <button
              onClick={handleSettingsClick}
              style={{
                background: 'rgba(255, 255, 255, 0.1)',
                border: '1px solid rgba(255, 255, 255, 0.3)',
                color: 'white',
                cursor: 'pointer',
                padding: '6px',
                borderRadius: '6px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: 'all 0.2s',
                fontSize: '14px',
                minWidth: '32px',
                minHeight: '32px'
              }}
              title="Paramètres"
            >
              <FiSettings size={14} />
            </button>
            <button
              onClick={handleExportClick}
              style={{
                background: 'rgba(255, 255, 255, 0.1)',
                border: '1px solid rgba(255, 255, 255, 0.3)',
                color: 'white',
                cursor: 'pointer',
                padding: '6px',
                borderRadius: '6px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: 'all 0.2s',
                fontSize: '14px',
                minWidth: '32px',
                minHeight: '32px'
              }}
              title="Exporter"
            >
              <FiDownload size={14} />
            </button>
            <button
              onClick={() => handleCloseClick(onToggle)}
              style={{
                background: 'rgba(255, 255, 255, 0.1)',
                border: '1px solid rgba(255, 255, 255, 0.3)',
                color: 'white',
                cursor: 'pointer',
                padding: '6px',
                borderRadius: '6px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: 'all 0.2s',
                fontSize: '14px',
                minWidth: '32px',
                minHeight: '32px'
              }}
              title="Fermer"
            >
              ✕
            </button>
          </div>
        </div>

        {showSettings && (
          <div className="settings-dropdown">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <h4 style={{ margin: 0 }}>Paramètres</h4>
              <button
                onClick={() => setShowSettings(false)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#6b7280',
                  cursor: 'pointer',
                  fontSize: '18px',
                  padding: '0',
                  width: '20px',
                  height: '20px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
                title="Fermer"
              >
                ×
              </button>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <label>
                <input type="checkbox" defaultChecked />
                Notifications
              </label>
              <label>
                <input type="checkbox" defaultChecked />
                Sons
              </label>
              <label>
                <input
                  type="checkbox"
                  checked={darkMode}
                  onChange={(e) => setDarkMode(e.target.checked)}
                />
                Mode sombre
              </label>
              <label>
                <input type="checkbox" />
                Auto-scroll
              </label>
              <label>
                <input type="checkbox" defaultChecked />
                Suggestions intelligentes
              </label>
            </div>
          </div>
        )}

        {showHistory && (
          <div className="settings-dropdown" style={{ minWidth: '250px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <h4 style={{ margin: 0 }}>Historique des conversations</h4>
              <button
                onClick={() => setShowHistory(false)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#6b7280',
                  cursor: 'pointer',
                  fontSize: '18px',
                  padding: '0',
                  width: '20px',
                  height: '20px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
                title="Fermer"
              >
                ×
              </button>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '200px', overflowY: 'auto' }}>
              <div style={{ padding: '8px', background: '#f8fafc', borderRadius: '4px', fontSize: '14px' }}>
                <div style={{ fontWeight: '500', marginBottom: '4px' }}>Aujourd'hui</div>
                <div style={{ color: '#6b7280', fontSize: '12px' }}>• Analyse des ventes Q4</div>
                <div style={{ color: '#6b7280', fontSize: '12px' }}>• Performance des produits</div>
              </div>
              <div style={{ padding: '8px', background: '#f8fafc', borderRadius: '4px', fontSize: '14px' }}>
                <div style={{ fontWeight: '500', marginBottom: '4px' }}>Hier</div>
                <div style={{ color: '#6b7280', fontSize: '12px' }}>• Segmentation client</div>
                <div style={{ color: '#6b7280', fontSize: '12px' }}>• Tendances mensuelles</div>
              </div>
            </div>
          </div>
        )}

        {showExport && (
          <div className="settings-dropdown" style={{ minWidth: '200px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <h4 style={{ margin: 0 }}>Exporter la conversation</h4>
              <button
                onClick={() => setShowExport(false)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#6b7280',
                  cursor: 'pointer',
                  fontSize: '18px',
                  padding: '0',
                  width: '20px',
                  height: '20px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
                title="Fermer"
              >
                ×
              </button>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <button style={{
                padding: '8px 12px',
                background: '#3b82f6',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '14px'
              }}>
                📄 Exporter en PDF
              </button>
              <button style={{
                padding: '8px 12px',
                background: '#10b981',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '14px'
              }}>
                📊 Exporter en CSV
              </button>
              <button style={{
                padding: '8px 12px',
                background: '#f59e0b',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '14px'
              }}>
                📋 Copier dans le presse-papiers
              </button>
            </div>
          </div>
        )}
      </div>

      <div className="chatbot-container" style={{ flex: 1, minHeight: 0 }}>
        <Chatbot
          config={config}
          actionProvider={ActionProvider}
          messageParser={MessageParser}
        />
      </div>
    </div>
  );
};

export default ChatBox;
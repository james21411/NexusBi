import React, { useState, useRef, useEffect } from 'react';
import ChatBox from './ChatBox/ChatBox';

const GlobalChatbot = ({ isOpen, collapsed, width, onToggle, onCollapse, onResize, sessionId, onSessionStart }) => {

  const handleMouseDown = (e) => {
    e.preventDefault();
    const startX = e.clientX;
    const startWidth = width;

    const handleMouseMove = (e) => {
      const dx = startX - e.clientX;
      let newWidth = startWidth + dx;
      if (newWidth < 260) newWidth = 260;
      if (newWidth > 640) newWidth = 640;
      onResize(newWidth);
    };

    const handleMouseUp = () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.userSelect = '';
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
    document.body.style.userSelect = 'none';
  };

  return (
    <>
      <button
        id="chatbotToggle"
        className="chatbot-toggle"
        onClick={onToggle}
        aria-controls="chatbotSidebar"
        aria-expanded={isOpen}
        title="Ouvrir le chatbot"
        style={{
          width: '60px',
          height: '60px',
          borderRadius: '50%',
          background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
          border: '3px solid #1e40af',
          color: 'white',
          fontSize: '24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: 'pointer',
          boxShadow: '0 4px 12px rgba(59, 130, 246, 0.4)',
          transition: 'all 0.3s ease',
          zIndex: 1000
        }}
        onMouseEnter={(e) => {
          e.target.style.transform = 'scale(1.1)';
          e.target.style.boxShadow = '0 6px 20px rgba(59, 130, 246, 0.6)';
        }}
        onMouseLeave={(e) => {
          e.target.style.transform = 'scale(1)';
          e.target.style.boxShadow = '0 4px 12px rgba(59, 130, 246, 0.4)';
        }}
      >
        <i className="fas fa-comments" aria-hidden="true"></i>
      </button>

      <aside
        id="chatbotSidebar"
        className={`chatbot-sidebar ${isOpen ? 'open' : ''} ${collapsed ? 'collapsed' : ''}`}
        style={{ width: `${width}px` }}
        aria-hidden={!isOpen}
      >

        <div id="chatResizer" className="chat-resizer" onMouseDown={handleMouseDown}></div>

        <div className="chatbot-content" style={{ height: '100%', width: '100%' }}>
          <ChatBox sessionId={sessionId} onSessionStart={onSessionStart} onToggle={onToggle} />
        </div>

      </aside>
    </>
  );
};

export default GlobalChatbot;
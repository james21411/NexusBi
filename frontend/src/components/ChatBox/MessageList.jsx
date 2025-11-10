import React from 'react';
import { FiUser, FiBot } from 'react-icons/fi';

const MessageList = ({ messages, messagesEndRef }) => {
  return (
    <div className="message-list">
      {messages.length === 0 ? (
        <div className="empty-state">
          <p>Start a conversation by asking a question about your data!</p>
          <div className="suggestions">
            <p>Try asking:</p>
            <ul>
              <li>"Show me total sales by region"</li>
              <li>"What are the top performing products?"</li>
              <li>"How have sales changed over time?"</li>
            </ul>
          </div>
        </div>
      ) : (
        messages.map((message) => (
          <div
            key={message.id}
            className={`message ${message.sender} ${message.isError ? 'error' : ''}`}
          >
            <div className="message-avatar">
              {message.sender === 'user' ? <FiUser /> : <FiBot />}
            </div>
            <div className="message-content">
              <div className="message-text">{message.text}</div>
              <div className="message-timestamp">
                {new Date(message.timestamp).toLocaleTimeString()}
              </div>
              {message.data && (
                <div className="message-data">
                  <details>
                    <summary>View Data</summary>
                    <pre>{JSON.stringify(message.data, null, 2)}</pre>
                  </details>
                </div>
              )}
            </div>
          </div>
        ))
      )}
      <div ref={messagesEndRef} />
    </div>
  );
};

export default MessageList;
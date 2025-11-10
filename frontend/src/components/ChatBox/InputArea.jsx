import React, { useState, useRef, useEffect } from 'react';
import { FiSend, FiLoader } from 'react-icons/fi';

const InputArea = ({ onSendMessage, isLoading, disabled }) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage('');
      adjustTextareaHeight();
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
    }
  };

  useEffect(() => {
    adjustTextareaHeight();
  }, [message]);

  return (
    <div className="input-area">
      <form onSubmit={handleSubmit} className="input-form">
        <div className="input-container">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask a question about your data..."
            disabled={disabled}
            rows={1}
            className="message-input"
          />
          <button
            type="submit"
            disabled={!message.trim() || disabled}
            className="send-button"
          >
            {isLoading ? (
              <FiLoader className="loading-spinner" />
            ) : (
              <FiSend />
            )}
          </button>
        </div>
      </form>

      <div className="input-hint">
        <small>
          Press Enter to send, Shift+Enter for new line
          {isLoading && " • Processing your request..."}
        </small>
      </div>
    </div>
  );
};

export default InputArea;
import React from "react";

import nexusBiIcon from "./NexusBi.png";

const BotAvatar = () => {
  return (
    <div className="react-chatbot-kit-chat-bot-avatar">
      <div className="react-chatbot-kit-chat-bot-avatar-container">
        <img src={nexusBiIcon} alt="NexusBi Bot" className="react-chatbot-kit-chat-bot-avatar-icon" />
      </div>
    </div>
  );
};

export default BotAvatar;
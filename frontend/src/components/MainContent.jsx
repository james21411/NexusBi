import React, { useState, useEffect } from 'react';
import TopMenuBar from './TopMenuBar';
import LeftNav from './LeftNav';
import ReportCanvas from './ReportCanvas';
import RightPane from './RightPane';
import GlobalChatbot from './GlobalChatbot';
import './MainContent.css';
import './TopMenuBar.css';

const MainContent = () => {
  const [currentPage, setCurrentPage] = useState('home');
  const [leftNavCollapsed, setLeftNavCollapsed] = useState(false);
  const [leftNavWidth, setLeftNavWidth] = useState(250);
  const [rightPaneOpen, setRightPaneOpen] = useState(false);
  const [chatbotOpen, setChatbotOpen] = useState(false);
  const [chatbotCollapsed, setChatbotCollapsed] = useState(false);
  const [chatbotWidth, setChatbotWidth] = useState(380);

  // Load persisted state on mount
  useEffect(() => {
    const collapsed = localStorage.getItem('leftNavCollapsed') === '1';
    const width = parseInt(localStorage.getItem('leftNavWidth')) || 250;
    const chatWidth = parseInt(localStorage.getItem('chatbotWidth')) || 380;

    setLeftNavCollapsed(collapsed);
    setLeftNavWidth(width);
    setChatbotWidth(chatWidth);
  }, []);

  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  const toggleLeftNav = () => {
    const newCollapsed = !leftNavCollapsed;
    setLeftNavCollapsed(newCollapsed);
    localStorage.setItem('leftNavCollapsed', newCollapsed ? '1' : '0');
  };

  const handleLeftNavResize = (width) => {
    setLeftNavWidth(width);
    setLeftNavCollapsed(false);
    localStorage.setItem('leftNavWidth', width.toString());
    localStorage.setItem('leftNavCollapsed', '0');
  };

  const toggleRightPane = () => {
    setRightPaneOpen(!rightPaneOpen);
  };

  const toggleChatbot = () => {
    setChatbotOpen(!chatbotOpen);
  };

  const handleChatbotCollapse = () => {
    const newCollapsed = !chatbotCollapsed;
    setChatbotCollapsed(newCollapsed);
  };

  const handleChatbotResize = (width) => {
    setChatbotWidth(width);
    localStorage.setItem('chatbotWidth', width.toString());
  };

  return (
    <div className="main-content-wrapper">
      <TopMenuBar
        onToggleLeftNav={toggleLeftNav}
        onToggleRightPane={toggleRightPane}
        currentPage={currentPage}
      />

      <LeftNav
        collapsed={leftNavCollapsed}
        width={leftNavWidth}
        currentPage={currentPage}
        onPageChange={handlePageChange}
        onToggle={toggleLeftNav}
        onResize={handleLeftNavResize}
      />

      <main className="main-content" style={{ marginLeft: leftNavCollapsed ? '72px' : `${leftNavWidth}px` }}>
        <ReportCanvas currentPage={currentPage} onPageChange={handlePageChange} />
      </main>

      <RightPane
        isOpen={rightPaneOpen}
        onClose={() => setRightPaneOpen(false)}
        onToggle={toggleRightPane}
      />

      <GlobalChatbot
        isOpen={chatbotOpen}
        collapsed={chatbotCollapsed}
        width={chatbotWidth}
        onToggle={toggleChatbot}
        onCollapse={handleChatbotCollapse}
        onResize={handleChatbotResize}
        sessionId={null}
        onSessionStart={() => {}}
      />
    </div>
  );
};

export default MainContent;
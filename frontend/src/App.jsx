import React, { useState } from 'react';
import Header from './components/Header';
import Footer from './components/Footer';
import MainContent from './components/MainContent';
import './styles/main.scss';

function App() {
  const [currentView, setCurrentView] = useState('dashboard');

  const handleViewChange = (view) => {
    setCurrentView(view);
  };

  return (
    <div className="App">
      <Header onViewChange={handleViewChange} currentView={currentView} />
      <MainContent />
      <Footer />
    </div>
  );
}

export default App;
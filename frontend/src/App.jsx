import React, { useState, useEffect } from 'react';
import './App.css';
import Header from './components/Header';
import Navigation from './components/Navigation';
import Dashboard from './components/Dashboard';
import FieldMap from './components/FieldMap';
import PredictionPanel from './components/PredictionPanel';
import DataUpload from './components/DataUpload';
import RasterAssets from './components/RasterAssets';
import { checkApiStatus } from './services/api';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [apiStatus, setApiStatus] = useState({ geo: false, ml: false, dis: false });
  const [notification, setNotification] = useState(null);

  useEffect(() => {
    checkApis();
    const interval = setInterval(checkApis, 30000);
    return () => clearInterval(interval);
  }, []);

  const checkApis = async () => {
    const status = await checkApiStatus();
    setApiStatus(status);
  };

  const showNotification = (message, type = 'info') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 5000);
  };

  return (
    <>
      <div className="bg-animation">
        <div className="grid-overlay"></div>
        <div className="orb orb1"></div>
        <div className="orb orb2"></div>
        <div className="orb orb3"></div>
      </div>

      {notification && (
        <div className={`notification ${notification.type}`}>
          {notification.message}
        </div>
      )}

      <div className="container">
        <Header apiStatus={apiStatus} onRefresh={checkApis} />
        <Navigation activeTab={activeTab} setActiveTab={setActiveTab} />
        
        <main>
          {activeTab === 'dashboard' && <Dashboard showNotification={showNotification} />}
          {activeTab === 'map' && <FieldMap showNotification={showNotification} />}
          {activeTab === 'prediction' && <PredictionPanel showNotification={showNotification} />}
          {activeTab === 'upload' && <DataUpload showNotification={showNotification} />}
          {activeTab === 'assets' && <RasterAssets showNotification={showNotification} />}
        </main>
      </div>
    </>
  );
}

export default App;
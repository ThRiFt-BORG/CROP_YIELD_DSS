import React from 'react';

export default function Navigation({ activeTab, setActiveTab }) {
  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'map', label: 'Field Map', icon: '🗺️' },
    { id: 'prediction', label: 'Predictions', icon: '📈' },
    { id: 'upload', label: 'Upload Data', icon: '⬆️' },
    { id: 'assets', label: 'Raster Assets', icon: '💾' }
  ];

  return (
    <nav>
      {tabs.map(tab => (
        <button
          key={tab.id}
          className={`nav-btn ${activeTab === tab.id ? 'active' : ''}`}
          onClick={() => setActiveTab(tab.id)}
        >
          <span style={{ fontSize: '20px' }}>{tab.icon}</span>
          <span>{tab.label}</span>
        </button>
      ))}
    </nav>
  );
}
import React from 'react';

export default function Header({ apiStatus, onRefresh }) {
  return (
    <header>
      <div className="header-content">
        <div className="logo">
          <div className="logo-icon">🌾</div>
          <div>
            <h1>Trans Nzoia DSS</h1>
            <p className="subtitle">AI-Powered Geospatial Agriculture Analytics</p>
          </div>
        </div>
        <div className="header-right">
          <div className="status-indicators">
            <StatusItem label="geo_api" online={apiStatus.geo} />
            <StatusItem label="ml_api" online={apiStatus.ml} />
            <StatusItem label="DIS" online={apiStatus.dis} />
          </div>
          <button className="refresh-btn" onClick={onRefresh} title="Refresh System Status">
            🔄
          </button>
        </div>
      </div>
    </header>
  );
}

function StatusItem({ label, online }) {
  return (
    <div className={`status-indicator ${online ? '' : 'offline'}`}>
      <div className="status-dot"></div>
      <span>{label}</span>
    </div>
  );
}
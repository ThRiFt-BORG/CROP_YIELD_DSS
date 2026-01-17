import React from 'react';

export default function Header({ apiStatus, onRefresh }) {
  return (
    <header>
      <div className="header-content">
        <div className="logo">
          <div className="logo-icon">🌾</div>
          <div>
            <h1>Crop Yield Decision Support System</h1>
            <p className="subtitle">AI-Powered Geospatial Agriculture Analytics Platform</p>
          </div>
        </div>
        <div className="header-right">
          <div className="status-indicators">
            <div className={`status-indicator ${apiStatus.geo ? '' : 'offline'}`}>
              <div className="status-dot"></div>
              <span>geo_api</span>
            </div>
            <div className={`status-indicator ${apiStatus.ml ? '' : 'offline'}`}>
              <div className="status-dot"></div>
              <span>ml_api</span>
            </div>
            <div className={`status-indicator ${apiStatus.dis ? '' : 'offline'}`}>
              <div className="status-dot"></div>
              <span>DIS-API</span>
            </div>
          </div>
          <button className="refresh-btn" onClick={onRefresh} title="Refresh">
            🔄
          </button>
        </div>
      </div>
    </header>
  );
}
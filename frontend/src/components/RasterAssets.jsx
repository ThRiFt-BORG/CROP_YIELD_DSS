import React, { useState, useEffect } from 'react';
import { fetchRasterAssets } from '../services/api';

export default function RasterAssets({ showNotification }) {
  const [assets, setAssets] = useState([]);

  useEffect(() => {
    loadAssets();
  }, []);

  const loadAssets = async () => {
    const data = await fetchRasterAssets();
    setAssets(data);
  };

  const handleView = (assetId) => {
    showNotification(`Viewing asset ${assetId}`, 'success');
  };

  return (
    <div className="data-table-container">
      <h3 className="section-title">💾 Raster Asset Catalog</h3>
      <div className="data-table">
        <table>
          <thead>
            <tr>
              <th>Asset ID</th>
              <th>Type</th>
              <th>Acquisition Date</th>
              <th>Format</th>
              <th>Size</th>
              <th>Region</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {assets.length === 0 ? (
              <tr><td colSpan="8" style={{ textAlign: 'center' }}>No assets</td></tr>
            ) : (
              assets.map(a => (
                <tr key={a.id}>
                  <td>AST-{String(a.id).padStart(4, '0')}</td>
                  <td>{a.type}</td>
                  <td>{a.acquisition_date}</td>
                  <td>{a.format}</td>
                  <td>{a.size}</td>
                  <td>{a.region || 'N/A'}</td>
                  <td><span className="status-active">✓ {a.status}</span></td>
                  <td>
                    <button 
                      className="chart-btn" 
                      onClick={() => handleView(a.id)}
                      style={{ padding: '6px 15px', fontSize: '12px' }}
                    >
                      View
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
import React, { useState, useEffect } from 'react';
import { fetchRegions, fetchRasterAssets, fetchPredictions } from '../services/api';
import YieldChart from './YieldChart';

export default function Dashboard({ showNotification }) {
  const [stats, setStats] = useState({ totalFields: 0, avgYield: 0, totalAssets: 0 });
  const [predictions, setPredictions] = useState([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [regions, assets, preds] = await Promise.all([
        fetchRegions(),
        fetchRasterAssets(),
        fetchPredictions()
      ]);
      
      const avgYield = preds.length > 0 
        ? (preds.reduce((sum, p) => sum + p.predicted_yield, 0) / preds.length).toFixed(1)
        : 0;
      
      setStats({ totalFields: regions.length, avgYield, totalAssets: assets.length });
      setPredictions(preds.slice(0, 10));
    } catch (error) {
      showNotification('Error loading data', 'error');
    }
  };

  return (
    <>
      <div className="dashboard-grid">
        <StatCard title="Total Fields" value={stats.totalFields} icon="🌾" change="+12%" />
        <StatCard title="Avg Yield" value={stats.avgYield} unit=" t/ha" icon="📊" change="+8.5%" />
        <StatCard title="Raster Assets" value={stats.totalAssets} icon="🛰️" change="+5.2%" />
        <StatCard title="ML Accuracy" value="94.2%" icon="🎯" change="+2.1%" />
      </div>

      <YieldChart />

      <div className="data-table-container">
        <h3 className="section-title">🔮 Recent Predictions</h3>
        <div className="data-table">
          <table>
            <thead>
              <tr>
                <th>Region ID</th>
                <th>Crop Type</th>
                <th>Predicted Yield</th>
                <th>Confidence</th>
                <th>Date</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {predictions.length === 0 ? (
                <tr><td colSpan="6" style={{ textAlign: 'center' }}>No predictions</td></tr>
              ) : (
                predictions.map((p, i) => (
                  <tr key={i}>
                    <td>{p.region_id}</td>
                    <td>{p.crop_type}</td>
                    <td>{p.predicted_yield} tons/ha</td>
                    <td>{p.confidence}%</td>
                    <td>{p.date}</td>
                    <td><span className="status-active">✓ {p.status}</span></td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}

function StatCard({ title, value, unit = '', icon, change }) {
  return (
    <div className="stat-card">
      <div className="stat-header">
        <div className="stat-title">{title}</div>
        <div className="stat-icon">{icon}</div>
      </div>
      <div className="stat-value">{value}{unit}</div>
      <div className="stat-change">
        <span className="change-value">{change}</span>
        <span className="change-text">from last period</span>
      </div>
    </div>
  );
}
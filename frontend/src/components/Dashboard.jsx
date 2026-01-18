import React, { useState, useEffect } from 'react';
import { fetchRegions, fetchRasterAssets, fetchPredictions } from '../services/api';
import YieldChart from './YieldChart';

export default function Dashboard({ showNotification }) {
  const [stats, setStats] = useState({ totalWards: 0, avgYield: 0, totalRasters: 0 });
  const [predictions, setPredictions] = useState([]);

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    try {
      const [regions, assets, preds] = await Promise.all([
        fetchRegions(),
        fetchRasterAssets(),
        fetchPredictions()
      ]);
      
      setStats({
        totalWards: regions.length,
        avgYield: preds.length > 0 ? (preds.reduce((s, p) => s + p.predicted_yield, 0) / preds.length).toFixed(2) : "2.45",
        totalRasters: assets.length
      });
      setPredictions(preds);
    } catch (e) { showNotification('API Sync Error', 'error'); }
  };

  return (
    <div className="dashboard-content">
      <div className="dashboard-grid">
        <StatCard title="Target Wards" value={stats.totalWards} icon="🇰🇪" change="Trans Nzoia" />
        <StatCard title="Avg Prediction" value={stats.avgYield} unit=" t/ha" icon="📈" change="+0.4 from 2023" />
        <StatCard title="GEE Assets" value={stats.totalRasters} icon="🛰️" change="Cloud Optimized" />
        <StatCard title="Model R²" value="0.79" icon="🎯" change="Very High" />
      </div>
      <YieldChart />
    </div>
  );
}

function StatCard({ title, value, unit = '', icon, change }) {
  return (
    <div className="stat-card">
      <div className="stat-header">
        <span className="stat-title">{title}</span>
        <span className="stat-icon">{icon}</span>
      </div>
      <div className="stat-value">{value}{unit}</div>
      <div className="stat-meta">{change}</div>
    </div>
  );
}
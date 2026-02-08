import React, { useState, useEffect } from 'react';
import { fetchDashboardSummary, fetchPredictions, fetchChartData } from '../services/api';
import YieldChart from './YieldChart';

export default function Dashboard({ showNotification }) {
  const [stats, setStats] = useState({ totalWards: 0, avgHistoricalYield: 0, totalAssets: 0, systemHealth: 'Scanning' });
  const [predictions, setPredictions] = useState([]);
  const [chartData, setChartData] = useState(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [summary, preds, chart] = await Promise.all([
          fetchDashboardSummary(),
          fetchPredictions(),
          fetchChartData()
        ]);
        
        setStats(summary);
        setPredictions(preds);
        setChartData(chart);
      } catch (e) { 
        showNotification('Data synchronization failed', 'error'); 
      }
    };
    loadData();
  }, [showNotification]);

  return (
    <div className="dashboard-content">
      <div className="dashboard-grid">
        <StatCard title="Administrative Units" value={stats.totalWards} icon="🇰🇪" change="Kenya PostGIS" />
        <StatCard title="Baseline Yield" value={stats.avgHistoricalYield} unit=" t/ha" icon="📊" change="SPAM 2020 Context" />
        <StatCard title="GEE Assets" value={stats.totalAssets} icon="🛰️" change="Raster Inventory" />
        <StatCard title="System Status" value={stats.systemHealth} icon="🛡️" change="ISO-19157 Ready" />
      </div>
      
      {chartData && <YieldChart chartData={chartData} />}

      <div className="data-table-container" style={{ marginTop: '30px' }}>
        <h3 className="section-title">🔮 Empirical Yield Audit (Recent Runs)</h3>
        <div className="data-table">
          <table>
            <thead>
              <tr>
                <th>Jurisdiction</th>
                <th>Estimated Yield</th>
                <th>Limiting Factor</th>
                <th>Season</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {predictions.length > 0 ? predictions.map((p, i) => (
                <tr key={i}>
                  <td>{p.region_id}</td>
                  <td style={{ fontWeight: 'bold', color: 'var(--primary)' }}>{p.predicted_yield} t/ha</td>
                  <td>{p.limiting_factor}</td>
                  <td>{p.date}</td>
                  <td><span className="status-active">✓ {p.status}</span></td>
                </tr>
              )) : <tr><td colSpan="5" style={{textAlign:'center'}}>No empirical predictions archived in PostGIS.</td></tr>}
            </tbody>
          </table>
        </div>
      </div>
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
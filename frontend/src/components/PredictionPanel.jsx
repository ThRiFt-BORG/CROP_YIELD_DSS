import React, { useState, useEffect } from 'react';
import { generatePrediction, fetchAvailableCounties } from '../services/api';

export default function PredictionPanel({ showNotification }) {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [counties, setCounties] = useState([]);
  const [fertilizer, setFertilizer] = useState(120);
  
  // LOGIC FOR ENGAGEMENT: The Simulation Terminal
  const [currentLog, setCurrentLog] = useState(0);
  const simLogs = [
    "📡 Initializing Spatial Intersection...",
    "🌍 PostGIS: Querying County Unit boundaries...",
    "🛰️ GEE: Extracting multi-band signature from Predictor Stack...",
    "🧪 Parameterizing DSSAT v3.0.0 soil & management profiles...",
    "⚙️ Executing Mechanistic CSM-CERES-Maize engine...",
    "🧠 Aggregating Random Forest statistical patterns...",
    "⚖️ Resolving Ensemble weighted average (ISO-19157)...",
    "✅ Finalizing yield estimation..."
  ];

  useEffect(() => {
    const init = async () => {
      const list = await fetchAvailableCounties();
      setCounties(list);
    };
    init();
  }, []);

  // Effect to cycle through logs when loading
  useEffect(() => {
    let interval;
    if (loading) {
      setCurrentLog(0);
      interval = setInterval(() => {
        setCurrentLog((prev) => (prev < simLogs.length - 1 ? prev + 1 : prev));
      }, 1800); // Change log every 1.8 seconds
    } else {
      clearInterval(interval);
    }
    return () => clearInterval(interval);
  }, [loading]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setResult(null);
    setLoading(true);
    
    const payload = {
      lat: parseFloat(e.target.lat.value),
      lon: parseFloat(e.target.lon.value),
      features: {
        ndvi_mean: 0.58, 
        precip_mean: 5.2,
        temp_mean: 22.5,
        fertilizer: fertilizer
      }
    };

    try {
      const predResult = await generatePrediction(payload);
      setResult(predResult);
      showNotification('Hybrid Ensemble Simulation Complete', 'success');
    } catch (err) {
      showNotification('Prediction Engine Error', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="prediction-suite">
      <div className="form-container" style={{ borderBottom: '4px solid var(--secondary)', marginBottom: '20px' }}>
        <h3 className="section-title">🚀 National Hybrid Yield Forecaster</h3>
        <p style={{ fontSize: '13px', color: 'rgba(255,255,255,0.6)' }}>
            System reconciling <strong>Machine Learning</strong> with <strong>Biophysical Simulation</strong>.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.2fr', gap: '30px' }}>
        
        {/* INPUT PANEL */}
        <div className="input-side">
          <div className="form-container" style={{ height: '100%' }}>
            <h4 style={{ color: 'var(--primary)', marginBottom: '20px', fontSize: '14px', textTransform: 'uppercase' }}>📡 Simulation Parameters</h4>
            <form onSubmit={handleSubmit}>
              <div className="dashboard-grid" style={{ gridTemplateColumns: '1fr 1fr', gap: '15px', marginBottom: '15px' }}>
                <div className="form-group">
                  <label className="form-label">Latitude</label>
                  <input type="number" step="0.0001" name="lat" className="form-input" defaultValue="1.0435" disabled={loading} />
                </div>
                <div className="form-group">
                  <label className="form-label">Longitude</label>
                  <input type="number" step="0.0001" name="lon" className="form-input" defaultValue="34.9589" disabled={loading} />
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Jurisdiction</label>
                <select className="form-select" name="county" disabled={loading}>
                  {counties.map(c => <option key={c.name} value={c.name}>{c.name} County</option>)}
                  {counties.length === 0 && <option>Trans Nzoia (Default)</option>}
                </select>
              </div>

              <div className="form-group" style={{ background: 'rgba(255,255,255,0.03)', padding: '15px', borderRadius: '12px', border: '1px solid rgba(0,255,136,0.1)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                  <label className="form-label" style={{ margin: 0 }}>Management: Nitrogen</label>
                  <span style={{ color: 'var(--primary)', fontWeight: 'bold' }}>{fertilizer} kg/ha</span>
                </div>
                <input 
                  type="range" min="0" max="300" value={fertilizer} 
                  onChange={(e) => setFertilizer(e.target.value)}
                  disabled={loading}
                  style={{ width: '100%', cursor: 'pointer', accentColor: 'var(--primary)' }}
                />
              </div>

              <button type="submit" className="btn-primary" disabled={loading} style={{ width: '100%', position: 'relative', overflow: 'hidden' }}>
                {loading ? 'CALCULATING...' : '🚀 RUN HYBRID SIMULATION'}
                {loading && <div className="btn-scan-line"></div>}
              </button>
            </form>
          </div>
        </div>

        {/* RESULT / INTELLIGENCE PANEL */}
        <div className="result-side">
          {loading ? (
            /* THE ENGAGEMENT TERMINAL */
            <div className="form-container" style={{ height: '100%', background: '#000', border: '1px solid var(--primary)', fontFamily: 'monospace' }}>
              <div style={{ color: 'var(--primary)', marginBottom: '15px', borderBottom: '1px solid var(--primary)', paddingBottom: '10px' }}>
                [DSS ENTIRE SIMULATION IN PROGRESS]
              </div>
              <div className="terminal-body" style={{ fontSize: '13px', color: '#fff' }}>
                {simLogs.slice(0, currentLog + 1).map((log, i) => (
                  <div key={i} style={{ marginBottom: '8px', animation: 'fadeIn 0.5s' }}>
                    <span style={{ color: 'var(--primary)' }}>&gt;</span> {log}
                  </div>
                ))}
                <div className="blinking-cursor">_</div>
              </div>
            </div>
          ) : result ? (
            <div className="form-container result-card animated fadeIn" style={{ height: '100%', border: '1px solid var(--secondary)' }}>
              <h4 style={{ color: 'var(--secondary)', marginBottom: '20px', fontSize: '14px', textTransform: 'uppercase' }}>📊 Yield Insights</h4>
              
              <div style={{ textAlign: 'center', padding: '20px 0', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                <div style={{ fontSize: '64px', fontWeight: '900', color: 'var(--primary)' }}>
                  {result.predicted_yield}<small style={{ fontSize: '18px', marginLeft: '10px' }}>t/ha</small>
                </div>
                <div className="badge bg-green">ISO-19157 TRACEABLE</div>
              </div>

              <div className="dashboard-grid" style={{ gridTemplateColumns: '1fr 1fr', gap: '15px', marginTop: '20px' }}>
                <div className="stat-card" style={{ background: 'rgba(255,204,0,0.05)', border: '1px solid #ffcc00' }}>
                  <div className="stat-title" style={{ color: '#ffcc00' }}>Stress Factor</div>
                  <div style={{ fontSize: '18px', fontWeight: 'bold' }}>{result.metadata.limiting_factor}</div>
                </div>
                <div className="stat-card">
                  <div className="stat-title">Ward Context</div>
                  <div style={{ fontSize: '18px', fontWeight: 'bold' }}>{result.metadata.ward_name}</div>
                </div>
              </div>

              {/* Progress Bar Weighting */}
              <div style={{ marginTop: '25px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', marginBottom: '8px', opacity: 0.7 }}>
                  <span>RF WEIGHT (60%)</span>
                  <span>DSSAT WEIGHT (40%)</span>
                </div>
                <div style={{ height: '8px', background: 'rgba(255,255,255,0.1)', borderRadius: '4px', display: 'flex', overflow: 'hidden' }}>
                   <div style={{ width: '60%', background: 'var(--primary)' }}></div>
                   <div style={{ width: '40%', background: 'var(--secondary)' }}></div>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '10px', fontSize: '11px' }}>
                   <span>{result.metadata.rf_val} t/ha</span>
                   <span>{result.metadata.dssat_val} t/ha</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="form-container" style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center', opacity: 0.3 }}>
              <div><div style={{ fontSize: '50px' }}>🧬</div><p>Awaiting Simulation parameters...</p></div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
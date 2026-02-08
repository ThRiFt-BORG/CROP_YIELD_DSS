import React, { useState, useEffect } from 'react';
import { generatePrediction, fetchAvailableCounties } from '../services/api';

// MOVE STATIC LOGS OUTSIDE: This fixes the ESLint 'simLogs.length' missing dependency warning
// It also makes the component more performant by not recreating the array on every render.
const SIM_LOGS = [
  "📡 Initializing Spatial Intersection...",
  "🌍 PostGIS: Querying County Unit boundaries...",
  "🛰️ GEE: Extracting multi-band signature from Predictor Stack...",
  "🧪 Parameterizing DSSAT v3.0.0 soil & management profiles...",
  "⚙️ Executing Mechanistic CSM-CERES-Maize engine...",
  "🧠 Aggregating Random Forest statistical patterns...",
  "⚖️ Resolving Ensemble weighted average (ISO-19157)...",
  "✅ Finalizing yield estimation..."
];

export default function PredictionPanel({ selectedPoint, showNotification }) {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [counties, setCounties] = useState([]);
  const [fertilizer, setFertilizer] = useState(120);
  const [currentLog, setCurrentLog] = useState(0);

  // Discovery: Load the list of counties available in PostGIS
  useEffect(() => {
    const init = async () => {
      const list = await fetchAvailableCounties();
      setCounties(list);
    };
    init();
  }, []);

  // ENGAGEMENT LOGIC: The Simulation Terminal Cycle
  useEffect(() => {
    let interval;
    if (loading) {
      setCurrentLog(0);
      interval = setInterval(() => {
        setCurrentLog((prev) => (prev < SIM_LOGS.length - 1 ? prev + 1 : prev));
      }, 1500); // Progress every 1.5 seconds for better engagement
    } else {
      clearInterval(interval);
    }
    return () => clearInterval(interval);
  }, [loading]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setResult(null);
    setLoading(true);
    
    // RECALIBRATION: Using props from the Map click to ensure we aren't stuck in Saboti
    const payload = {
      lat: selectedPoint.lat,
      lon: selectedPoint.lon,
      features: {
        fertilizer: fertilizer,
        // Backend default year handles the temporal dimension if not specified
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
      {/* HEADER: Logic & Methodology Explainer */}
      <div className="form-container" style={{ borderBottom: '4px solid var(--secondary)', marginBottom: '20px' }}>
        <h3 className="section-title">🚀 National Hybrid Yield Forecaster</h3>
        <p style={{ fontSize: '13px', color: 'rgba(255,255,255,0.6)', lineHeight: '1.6' }}>
            System reconciling <strong>Statistical Machine Learning (Random Forest)</strong> with 
            <strong> Mechanistic Biophysics (DSSAT v3.0.0)</strong>. Processes multi-band geospatial 
            vitals to provide ISO-19157 compliant decision support for Kenya.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.2fr', gap: '30px' }}>
        
        {/* INPUT PANEL: Spatial & Management Controllers */}
        <div className="input-side">
          <div className="form-container" style={{ height: '100%' }}>
            <h4 style={{ color: 'var(--primary)', marginBottom: '20px', fontSize: '12px', textTransform: 'uppercase' }}>📡 Simulation Parameters</h4>
            <form onSubmit={handleSubmit}>
              <div className="dashboard-grid" style={{ gridTemplateColumns: '1fr 1fr', gap: '15px', marginBottom: '15px' }}>
                <div className="form-group">
                  <label className="form-label">Latitude (Synced)</label>
                  <input 
                    type="number" 
                    name="lat" 
                    className="form-input" 
                    value={selectedPoint.lat} 
                    readOnly 
                    style={{ background: 'rgba(0,255,136,0.03)', cursor: 'not-allowed' }}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Longitude (Synced)</label>
                  <input 
                    type="number" 
                    name="lon" 
                    className="form-input" 
                    value={selectedPoint.lon} 
                    readOnly 
                    style={{ background: 'rgba(0,255,136,0.03)', cursor: 'not-allowed' }}
                  />
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Active Jurisdiction</label>
                <select className="form-select" name="county" disabled={loading}>
                  {counties.length > 0 ? (
                    counties.map(c => <option key={c.name} value={c.name}>{c.name} County</option>)
                  ) : (
                    <option>Trans Nzoia (Default)</option>
                  )}
                </select>
              </div>

              {/* DYNAMIC FERTILIZER SLIDER: Drives the Nitrogen Response logic */}
              <div className="form-group" style={{ background: 'rgba(255,255,255,0.03)', padding: '15px', borderRadius: '12px', border: '1px solid rgba(0,255,136,0.1)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                  <label className="form-label" style={{ margin: 0 }}>Nitrogen (Fertilizer)</label>
                  <span style={{ color: 'var(--primary)', fontWeight: 'bold' }}>{fertilizer} kg/ha</span>
                </div>
                <input 
                  type="range" 
                  min="0" max="300" 
                  value={fertilizer} 
                  onChange={(e) => setFertilizer(parseInt(e.target.value))}
                  disabled={loading}
                  style={{ width: '100%', cursor: 'pointer', accentColor: 'var(--primary)' }}
                />
                <p style={{ fontSize: '10px', opacity: 0.5, marginTop: '8px' }}>* Adjust to simulate yield response via Mechanistic engine.</p>
              </div>

              <button type="submit" className="btn-primary" disabled={loading} style={{ width: '100%', position: 'relative', overflow: 'hidden' }}>
                {loading ? 'ANALYZING BIOPHYSICS...' : '🚀 RUN HYBRID SIMULATION'}
                {loading && <div className="btn-scan-line"></div>}
              </button>
            </form>
          </div>
        </div>

        {/* RESULT / INTELLIGENCE PANEL: Terminal and Stat Cards */}
        <div className="result-side">
          {loading ? (
            /* THE HIGH-TECH TERMINAL OVERLAY */
            <div className="form-container" style={{ height: '100%', background: '#000', border: '1px solid var(--primary)', fontFamily: 'monospace', position: 'relative' }}>
              <div style={{ color: 'var(--primary)', marginBottom: '15px', borderBottom: '1px solid var(--primary)', paddingBottom: '10px' }}>
                [DSS ENTIRE SIMULATION IN PROGRESS]
              </div>
              <div className="terminal-body" style={{ fontSize: '13px', color: '#fff' }}>
                {SIM_LOGS.slice(0, currentLog + 1).map((log, i) => (
                  <div key={i} style={{ marginBottom: '8px', animation: 'fadeIn 0.5s' }}>
                    <span style={{ color: 'var(--primary)' }}>&gt;</span> {log}
                  </div>
                ))}
                <div className="blinking-cursor">_</div>
              </div>
              <div className="terminal-background-glow"></div>
            </div>
          ) : result ? (
            /* EMPIRICAL RESULTS DISPLAY */
            <div className="form-container result-card animated fadeIn" style={{ height: '100%', border: '1px solid var(--secondary)' }}>
              <h4 style={{ color: 'var(--secondary)', marginBottom: '20px', fontSize: '12px', textTransform: 'uppercase' }}>📊 Intelligent Forecast</h4>
              
              <div style={{ textAlign: 'center', padding: '20px 0', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                <div style={{ fontSize: '12px', textTransform: 'uppercase', opacity: 0.6 }}>Estimated Empirical Yield</div>
                <div style={{ fontSize: '64px', fontWeight: '900', color: 'var(--primary)', textShadow: '0 0 20px rgba(0,255,136,0.3)' }}>
                  {result.predicted_yield}
                  <small style={{ fontSize: '18px', color: '#fff', marginLeft: '10px' }}>t/ha</small>
                </div>
                <div className="badge bg-green" style={{ marginTop: '10px' }}>ISO-19157 TRACEABLE</div>
              </div>

              <div className="dashboard-grid" style={{ gridTemplateColumns: '1fr 1fr', gap: '15px', marginTop: '20px' }}>
                <div className="stat-card" style={{ background: 'rgba(255,204,0,0.05)', border: '1px solid #ffcc00', padding: '20px' }}>
                  <div className="stat-title" style={{ color: '#ffcc00' }}>Limiting Factor</div>
                  <div style={{ fontSize: '18px', fontWeight: 'bold', marginTop: '5px' }}>{result.metadata.factor || "Optimal Growth"}</div>
                </div>
                <div className="stat-card" style={{ padding: '20px' }}>
                  <div className="stat-title">Ward Context</div>
                  <div style={{ fontSize: '18px', fontWeight: 'bold', marginTop: '5px' }}>{result.metadata.ward_name}</div>
                </div>
              </div>

              {/* Ensemble Weighting Visualization */}
              <div style={{ marginTop: '25px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', marginBottom: '8px', opacity: 0.7 }}>
                  <span>RF STATISTICAL WEIGHT (60%)</span>
                  <span>DSSAT MECHANISTIC WEIGHT (40%)</span>
                </div>
                <div style={{ height: '8px', background: 'rgba(255,255,255,0.1)', borderRadius: '4px', display: 'flex', overflow: 'hidden' }}>
                   <div style={{ width: '60%', background: 'var(--primary)' }}></div>
                   <div style={{ width: '40%', background: 'var(--secondary)' }}></div>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '10px', fontSize: '12px' }}>
                   <span style={{ color: 'var(--primary)', fontWeight: 'bold' }}>{result.metadata.rf} t/ha</span>
                   <span style={{ color: 'var(--secondary)', fontWeight: 'bold' }}>{result.metadata.dssat} t/ha</span>
                </div>
              </div>
            </div>
          ) : (
            /* INITIAL STATE */
            <div className="form-container" style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center', opacity: 0.3 }}>
              <div>
                <div style={{ fontSize: '60px', marginBottom: '20px' }}>🧬</div>
                <p>Select a county unit on the map<br/>and click Run Hybrid Simulation.</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
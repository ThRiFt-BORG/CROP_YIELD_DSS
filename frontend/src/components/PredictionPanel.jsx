import React, { useState, useEffect } from 'react';
import { fetchRegions, generatePrediction } from '../services/api';

export default function PredictionPanel({ showNotification }) {
  const [regions, setRegions] = useState([]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => { loadRegions(); }, []);
  const loadRegions = async () => { const data = await fetchRegions(); setRegions(data); };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    // DATA INTEGRITY: Collecting precise coordinates for the PostGIS Spatial Join
    const payload = {
      lat: parseFloat(e.target.lat.value),
      lon: parseFloat(e.target.lon.value),
      features: {
        ndvi_mean: 0.58, // This should eventually come from the GEE raster
        precip_mean: 5.2,
        temp_mean: 22.5,
        fertilizer: parseFloat(e.target.fertilizer.value) || 100
      }
    };

    const predResult = await generatePrediction(payload);
    setResult(predResult);
    setLoading(false);
    if (predResult) showNotification('Ensemble Prediction Complete', 'success');
  };

  return (
    <>
      <div className="form-container">
        <h3 className="section-title">🎯 Hybrid Simulation Engine</h3>
        <form onSubmit={handleSubmit}>
          <div className="dashboard-grid" style={{ gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
            <div className="form-group">
              <label className="form-label">Latitude</label>
              <input type="number" step="0.0001" name="lat" className="form-input" defaultValue="1.0435" />
            </div>
            <div className="form-group">
              <label className="form-label">Longitude</label>
              <input type="number" step="0.0001" name="lon" className="form-input" defaultValue="34.9589" />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Management: Fertilizer (kg/ha)</label>
            <input type="number" name="fertilizer" className="form-input" defaultValue="120" />
          </div>

          <button type="submit" className="btn-primary" disabled={loading} style={{ width: '100%' }}>
            <span>{loading ? '⏳ Calculating ISO Yield...' : '🚀 Run Hybrid Prediction'}</span>
          </button>
        </form>
      </div>

      {result && (
        <div className="form-container result-card animated fadeIn">
          <h3 className="section-title" style={{ color: 'var(--secondary)' }}>📊 Model Insights</h3>
          <div className="dashboard-grid" style={{ marginBottom: 0 }}>
            {/* Main Prediction Value */}
            <div className="stat-card" style={{ borderLeft: '4px solid var(--primary)' }}>
              <div className="stat-title">Final Yield Estimate</div>
              <div className="stat-value" style={{ fontSize: '48px' }}>{result.predicted_yield} <small style={{ fontSize: '14px', color: '#fff' }}>t/ha</small></div>
            </div>

            {/* Hybrid Breakdown - ONLY possible with Recalibrated code */}
            {result.metadata && (
              <div className="stat-card">
                <div className="stat-title">Model Confidence</div>
                <div style={{ marginTop: '10px' }}>
                  <p className="change-text">RF Statistical: <span className="change-value">{result.metadata.rf_val} t/ha</span></p>
                  <p className="change-text">DSSAT Mechanistic: <span className="change-value">{result.metadata.dssat_val} t/ha</span></p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}
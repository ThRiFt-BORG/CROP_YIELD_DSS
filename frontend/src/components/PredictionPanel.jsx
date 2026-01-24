import React, { useState } from 'react';
import { generatePrediction } from '../services/api';

export default function PredictionPanel({ showNotification }) {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    const payload = {
      lat: parseFloat(e.target.lat.value),
      lon: parseFloat(e.target.lon.value),
      features: {
        ndvi_mean: 0.58, 
        precip_mean: 5.2,
        temp_mean: 22.5,
        fertilizer: parseFloat(e.target.fertilizer.value) || 120
      }
    };

    try {
      const predResult = await generatePrediction(payload);
      setResult(predResult);
      showNotification('County Prediction Complete', 'success');
    } catch (err) {
      showNotification('Prediction Engine Error', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="form-container">
        <h3 className="section-title">🎯 Hybrid County Simulation Engine</h3>
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
          <h3 className="section-title" style={{ color: 'var(--secondary)' }}>📊 County-Level Insights</h3>
          <div className="dashboard-grid" style={{ marginBottom: 0 }}>
            <div className="stat-card" style={{ borderLeft: '4px solid var(--primary)' }}>
              <div className="stat-title">Final Yield Estimate</div>
              <div className="stat-value" style={{ fontSize: '48px' }}>{result.predicted_yield} <small style={{ fontSize: '14px', color: '#fff' }}>t/ha</small></div>
            </div>

            {result.metadata && (
              <div className="stat-card">
                <div className="stat-title">Diagnostic: {result.metadata.limiting_factor}</div>
                <div style={{ marginTop: '10px' }}>
                  <p className="change-text">RF Statistical: <span className="change-value">{result.metadata.rf_val} t/ha</span></p>
                  <p className="change-text">DSSAT Mechanistic: <span className="change-value">{result.metadata.dssat_val} t/ha</span></p>
                  <p style={{fontSize: '11px', color: 'var(--primary)', marginTop: '10px', fontWeight: 'bold'}}>
                    DSS Advice: {result.metadata.limiting_factor.includes('Water') ? 'Prioritize Irrigation' : 'Normal Operations'}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}
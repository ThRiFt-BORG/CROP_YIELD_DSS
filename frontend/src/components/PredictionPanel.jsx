import React, { useState, useEffect } from 'react';
import { fetchRegions, generatePrediction } from '../services/api';

export default function PredictionPanel({ showNotification }) {
  const [regions, setRegions] = useState([]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadRegions();
  }, []);

  const loadRegions = async () => {
    const data = await fetchRegions();
    setRegions(data);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    const formData = {
      region_id: e.target.region.value,
      crop_type: e.target.crop.value,
      season: e.target.season.value
    };

    const predResult = await generatePrediction(formData);
    setResult(predResult);
    setLoading(false);
    showNotification('Prediction generated', 'success');
  };

  return (
    <>
      <div className="form-container">
        <h3 className="section-title">🎯 Generate Yield Prediction</h3>
        <form onsubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Select Region</label>
            <select className="form-select" name="region" required>
              <option value="">Choose a field...</option>
              {regions.map(r => <option key={r.id} value={r.id}>{r.name}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Crop Type</label>
            <select className="form-select" name="crop" required>
              <option value="">Select crop...</option>
              <option value="wheat">Wheat</option>
              <option value="corn">Corn</option>
              <option value="rice">Rice</option>
              <option value="soybean">Soybean</option>
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Season</label>
            <select className="form-select" name="season">
              <option value="spring">Spring</option>
              <option value="summer">Summer</option>
              <option value="fall">Fall</option>
              <option value="winter">Winter</option>
            </select>
          </div>
          <button type="submit" className="btn-primary" disabled={loading}>
            <span>🎯</span>
            <span>{loading ? 'Generating...' : 'Generate Prediction'}</span>
          </button>
        </form>
      </div>

      {result && (
        <div className="form-container">
          <h3 className="section-title">📊 Prediction Results</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px' }}>
            <ResultItem label="Predicted Yield" value={`${result.predicted_yield} t/ha`} />
            <ResultItem label="Confidence" value={`${result.confidence}%`} />
            <ResultItem label="Expected Range" value={`${result.range_min}-${result.range_max} t/ha`} />
            <ResultItem label="Risk Level" value={result.risk} />
          </div>
        </div>
      )}
    </>
  );
}

function ResultItem({ label, value }) {
  return (
    <div style={{ textAlign: 'center' }}>
      <div style={{ color: 'rgba(255,255,255,0.6)', fontSize: '13px', marginBottom: '8px' }}>{label}</div>
      <div style={{ fontSize: '32px', fontWeight: '800', color: 'var(--primary)' }}>{value}</div>
    </div>
  );
}
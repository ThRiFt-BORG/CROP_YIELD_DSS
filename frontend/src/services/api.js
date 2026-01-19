export const API_BASE = {
  GEO: 'http://localhost:8000/v1',
  ML: 'http://localhost:8001/v1',
  DIS: 'http://localhost:8002/v1'
};

/**
 * Checks health of all Docker containers
 */
export async function checkApiStatus() {
  const status = { geo: false, ml: false, dis: false };
  // Geo uses /v1/status
  try { status.geo = (await fetch(`${API_BASE.GEO}/status`)).ok; } catch (e) {}
  // ML uses /health (standardized in our last main.py fix)
  try { status.ml = (await fetch(`http://localhost:8001/health`)).ok; } catch (e) {}
  // DIS uses /v1/status
  try { status.dis = (await fetch(`${API_BASE.DIS}/status`)).ok; } catch (e) {}
  return status;
}

export async function fetchRegions() {
  try {
    const res = await fetch(`${API_BASE.GEO}/regions`);
    if (res.ok) return await res.json();
  } catch (e) { console.error("Geo API error", e); }
  // Robust fallback for Trans Nzoia ROI
  return [{ id: 'trans_nzoia', name: 'Trans Nzoia County', area: '2,499 km²', crop: 'Maize' }];
}

export async function fetchRasterAssets() {
  try {
    const res = await fetch(`${API_BASE.DIS}/rasters`);
    if (res.ok) return await res.json();
  } catch (e) { console.error("Raster API error", e); }
  return [];
}

export async function fetchPredictions() {
  try {
    const res = await fetch(`${API_BASE.ML}/predictions`);
    if (res.ok) return await res.json();
  } catch (e) { console.error("ML Predictions error", e); }
  return [];
}

/**
 * GENERATE PREDICTION
 * Recalibrated to ensure coordinates are inside 'features' for the Python backend
 */
export async function generatePrediction(payload) {
  try {
    const formattedPayload = {
      features: {
        ...payload.features,
        lat: payload.lat,
        lon: payload.lon
      }
    };

    const res = await fetch(`${API_BASE.ML}/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formattedPayload)
    });
    if (res.ok) return await res.json();
  } catch (e) { console.error("Prediction failed", e); }
  return null;
}

/**
 * UPLOAD RASTER
 * Correctly packages flat form data into the JSON-metadata structure DIS expects
 */
export async function uploadRaster(formData) {
  try {
    const disPayload = new FormData();
    // formData.get('file') refers to the <input name="file"> in DataUpload.jsx
    disPayload.append('file', formData.get('file'));

    const metadata = {
      asset_type: formData.get('data_type') || 'PredictorStack',
      datetime: new Date(formData.get('date')).toISOString(),
      crop_id: "Maize"
    };
    disPayload.append('metadata', JSON.stringify(metadata));

    const res = await fetch(`${API_BASE.DIS}/ingest`, { 
      method: 'POST', 
      body: disPayload 
    });
    return res.ok;
  } catch (e) { 
    console.error("Raster upload network error", e);
    return false; 
  }
}

export async function uploadCSV(file, type) {
  try {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE.DIS}/ingest/csv/${type}`, { 
      method: 'POST', 
      body: formData 
    });
    return res.ok;
  } catch (e) { 
    console.error("CSV upload network error", e);
    return false; 
  }
}
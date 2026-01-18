export const API_BASE = {
  GEO: 'http://localhost:8000/v1',
  ML: 'http://localhost:8001/v1',
  DIS: 'http://localhost:8002/v1'
};

export async function checkApiStatus() {
  const status = { geo: false, ml: false, dis: false };
  try { status.geo = (await fetch(`http://localhost:8000/v1/status`)).ok; } catch (e) {}
  try { status.ml = (await fetch(`http://localhost:8001/health`)).ok; } catch (e) {}
  try { status.dis = (await fetch(`http://localhost:8002/v1/status`)).ok; } catch (e) {}
  return status;
}

export async function fetchRegions() {
  try {
    const res = await fetch(`${API_BASE.GEO}/regions`);
    if (res.ok) return await res.json();
  } catch (e) { console.error("Geo API error", e); }
  return [{ id: 'trans_nzoia', name: 'Trans Nzoia County', area: '249k ha', crop: 'Maize' }];
}

// FIX: Added missing function
export async function fetchRasterAssets() {
  try {
    const res = await fetch(`${API_BASE.DIS}/rasters`); // Update this if your DIS has a different route
    if (res.ok) return await res.json();
  } catch (e) { console.error("Raster API error", e); }
  return [];
}

// FIX: Added missing function
export async function fetchPredictions() {
  try {
    const res = await fetch(`${API_BASE.ML}/predictions`);
    if (res.ok) return await res.json();
  } catch (e) { console.error("ML Predictions error", e); }
  return [];
}

export async function generatePrediction(payload) {
  try {
    const res = await fetch(`${API_BASE.ML}/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (res.ok) return await res.json();
  } catch (e) { console.error("Prediction failed", e); }
  return null;
}

export async function uploadRaster(formData) {
  try {
    const metadata = {
      asset_type: formData.get('data_type') || 'PredictorStack',
      datetime: new Date(formData.get('date')).toISOString(),
      crop_id: "Maize"
    };
    const disPayload = new FormData();
    disPayload.append('file', formData.get('file'));
    disPayload.append('metadata', JSON.stringify(metadata));
    const res = await fetch(`${API_BASE.DIS}/ingest`, { method: 'POST', body: disPayload });
    return res.ok;
  } catch (e) { return false; }
}

export async function uploadCSV(file, type) {
  try {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE.DIS}/ingest/csv/${type}`, { method: 'POST', body: formData });
    return res.ok;
  } catch (e) { return false; }
}
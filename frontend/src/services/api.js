export const API_BASE = {
  GEO: 'http://localhost:8000',
  ML: 'http://localhost:8001',
  DIS: 'http://localhost:8002'
};

export async function checkApiStatus() {
  const status = { geo: false, ml: false, dis: false };
  
  try {
    const geoRes = await fetch(`${API_BASE.GEO}/health`, { method: 'GET' });
    status.geo = geoRes.ok;
  } catch (e) {}
  
  try {
    const mlRes = await fetch(`${API_BASE.ML}/health`, { method: 'GET' });
    status.ml = mlRes.ok;
  } catch (e) {}
  
  try {
    const disRes = await fetch(`${API_BASE.DIS}/health`, { method: 'GET' });
    status.dis = disRes.ok;
  } catch (e) {}
  
  return status;
}

export async function fetchRegions() {
  try {
    const res = await fetch(`${API_BASE.GEO}/regions`);
    if (res.ok) return await res.json();
  } catch (e) {}
  return [
    { id: 1, name: 'Field Alpha', geometry: [[40.7128, -74.0060], [40.7138, -74.0050], [40.7148, -74.0070], [40.7128, -74.0060]], area: '25 ha', crop: 'Wheat' },
    { id: 2, name: 'Field Beta', geometry: [[40.7200, -74.0100], [40.7210, -74.0090], [40.7220, -74.0110], [40.7200, -74.0100]], area: '18 ha', crop: 'Corn' }
  ];
}

export async function fetchRasterAssets() {
  try {
    const res = await fetch(`${API_BASE.DIS}/rasters`);
    if (res.ok) return await res.json();
  } catch (e) {}
  return [
    { id: 1, type: 'NDVI', acquisition_date: '2026-01-10', format: 'COG', size: '45 MB', region: 'Field Alpha', status: 'Active' },
    { id: 2, type: 'Precipitation', acquisition_date: '2026-01-12', format: 'GeoTIFF', size: '32 MB', region: 'Field Beta', status: 'Active' }
  ];
}

export async function fetchPredictions() {
  try {
    const res = await fetch(`${API_BASE.ML}/predictions`);
    if (res.ok) return await res.json();
  } catch (e) {}
  return [
    { region_id: 'REG-001', crop_type: 'Wheat', predicted_yield: 4.5, confidence: 92, date: '2026-01-15', status: 'Active' },
    { region_id: 'REG-002', crop_type: 'Corn', predicted_yield: 5.2, confidence: 89, date: '2026-01-14', status: 'Active' }
  ];
}

export async function generatePrediction(data) {
  try {
    const res = await fetch(`${API_BASE.ML}/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (res.ok) return await res.json();
  } catch (e) {}
  return {
    predicted_yield: (Math.random() * 2 + 4).toFixed(2),
    confidence: Math.floor(Math.random() * 10 + 85),
    range_min: 3.5,
    range_max: 5.5,
    risk: 'Low'
  };
}

export async function uploadRaster(formData) {
  try {
    const res = await fetch(`${API_BASE.DIS}/upload`, {
      method: 'POST',
      body: formData
    });
    return res.ok;
  } catch (e) {
    return false;
  }
}
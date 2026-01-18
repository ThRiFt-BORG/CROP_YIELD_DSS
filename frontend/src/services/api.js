export const API_BASE = {
  GEO: 'http://localhost:8000/v1', // Added /v1 to match your FastAPI routers
  ML: 'http://localhost:8001/v1',
  DIS: 'http://localhost:8002/v1'
};

/**
 * Verifies if all Docker containers are reachable
 */
export async function checkApiStatus() {
  const status = { geo: false, ml: false, dis: false };
  
  try {
    // Geo uses default status
    const geoRes = await fetch(`${API_BASE.GEO}/status`);
    status.geo = geoRes.ok;
  } catch (e) {}
  
  try {
    // ML uses /health from main.py
    const mlRes = await fetch(`http://localhost:8001/health`);
    status.ml = mlRes.ok;
  } catch (e) {}
  
  try {
    // DIS uses /v1/status from main.py
    const disRes = await fetch(`${API_BASE.DIS}/status`);
    status.dis = disRes.ok;
  } catch (e) {}
  
  return status;
}

export async function fetchRegions() {
  try {
    const res = await fetch(`${API_BASE.GEO}/regions`);
    if (res.ok) return await res.json();
  } catch (e) {
    console.error("GEO API unavailable, using local mock data.");
  }
  return [
    { id: 'trans_nzoia', name: 'Trans Nzoia County', area: '249,000 ha', crop: 'Maize' }
  ];
}

/**
 * UPLOAD RASTER (GEOTIFF/COG)
 * Connects to DIS Service /v1/ingest
 */
export async function uploadRaster(formData) {
  try {
    // RECALIBRATION: DIS backend expects a "metadata" field containing a JSON string
    // We transform the flat formData into the structure DIS expects
    const metadata = {
      asset_type: formData.get('data_type'),
      datetime: new Date(formData.get('acquisition_date')).toISOString(),
      crop_id: "Maize"
    };

    const disPayload = new FormData();
    disPayload.append('file', formData.get('file'));
    disPayload.append('metadata', JSON.stringify(metadata));

    const res = await fetch(`${API_BASE.DIS}/ingest`, {
      method: 'POST',
      body: disPayload
    });
    return res.ok;
  } catch (e) {
    console.error("Raster Ingestion Error:", e);
    return false;
  }
}

/**
 * UPLOAD CSV (GEE Zonal Stats or ML Samples)
 * Connects to DIS Service /v1/ingest/csv/{type}
 */
export async function uploadCSV(file, type) {
  try {
    const formData = new FormData();
    formData.append('file', file);

    // type is either 'wards' or 'samples'
    const res = await fetch(`${API_BASE.DIS}/ingest/csv/${type}`, {
      method: 'POST',
      body: formData
    });
    return res.ok;
  } catch (e) {
    console.error("CSV Ingestion Error:", e);
    return false;
  }
}

export async function generatePrediction(features) {
  try {
    const res = await fetch(`${API_BASE.ML}/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ features })
    });
    if (res.ok) return await res.json();
  } catch (e) {
    console.error("ML Prediction Error:", e);
  }
  return null;
}
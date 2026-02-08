/**
 * Trans Nzoia County Crop Yield DSS - API Bridge
 * Recalibrated for National Scale (47 Counties) and Multi-temporal analysis.
 */

export const API_BASE = {
  GEO: 'http://localhost:8000/v1',
  ML: 'http://localhost:8001/v1',
  DIS: 'http://localhost:8002/v1'
};

/**
 * Checks health of all Docker containers using standardized health routes.
 * Geo/DIS use /v1/status | ML uses /health
 */
export async function checkApiStatus() {
  const status = { geo: false, ml: false, dis: false };
  try { status.geo = (await fetch(`${API_BASE.GEO}/status`)).ok; } catch (e) {}
  try { status.ml = (await fetch(`http://localhost:8001/health`)).ok; } catch (e) {}
  try { status.dis = (await fetch(`${API_BASE.DIS}/status`)).ok; } catch (e) {}
  return status;
}

/**
 * Discovery: Returns all counties currently in PostGIS for the Map Switcher.
 */
export async function fetchAvailableCounties() {
  try {
    const res = await fetch(`${API_BASE.GEO}/counties`);
    if (res.ok) return await res.json();
  } catch (e) { console.error("Geospatial counties discovery error", e); }
  return [];
}

/**
 * Discovery: Returns all production years available in database for the Temporal Filter.
 */
export async function fetchAvailableYears() {
  try {
    const res = await fetch(`${API_BASE.GEO}/years`);
    if (res.ok) return await res.json();
  } catch (e) { console.error("Temporal years discovery error", e); }
  return [];
}

/**
 * Aggregates: Fetches real PostGIS aggregates for the Dashboard StatCards.
 * Returns total units, mean SPAM yield, and asset counts.
 */
export async function fetchDashboardSummary() {
  try {
    const res = await fetch(`${API_BASE.GEO}/dashboard/summary`);
    if (res.ok) return await res.json();
  } catch (e) { console.error("Dashboard summary aggregation error", e); }
  return { totalWards: 0, avgHistoricalYield: 0, totalAssets: 0, systemHealth: "Offline" };
}

/**
 * Comparative Data: Fetches Potential (SPAM 2020) vs Predicted (2024) for the Gap Analysis Chart.
 */
export async function fetchChartData() {
  try {
    const res = await fetch(`${API_BASE.GEO}/dashboard/chart`);
    if (res.ok) return await res.json();
  } catch (e) { console.error("Yield Gap chart data error", e); }
  return { labels: [], datasets: [] };
}

/**
 * Spatial: Pulls unit boundaries from PostGIS.
 * Supports dynamic County and Production Year filtering.
 */
export async function fetchRegions(county = null, year = 2024) {
  try {
    let url = `${API_BASE.GEO}/regions?year=${year}`;
    if (county) url += `&county=${encodeURIComponent(county)}`;
    const res = await fetch(url);
    if (res.ok) return await res.json();
  } catch (e) { console.error("Regional boundaries fetch error", e); }
  return [];
}

/**
 * Assets: Lists all GEE Raster Stacks registered in the system.
 */
export async function fetchRasterAssets() {
  try {
    const res = await fetch(`${API_BASE.DIS}/rasters`);
    if (res.ok) return await res.json();
  } catch (e) { console.error("Raster asset registry error", e); }
  return [];
}

/**
 * History: Returns recent hybrid predictions persisted in PostGIS.
 */
export async function fetchPredictions() {
  try {
    const res = await fetch(`${API_BASE.ML}/predictions`);
    if (res.ok) return await res.json();
  } catch (e) { console.error("Prediction history fetch error", e); }
  return [];
}

/**
 * Simulation: Calls the ML-API Hybrid Ensemble.
 * Recalibrated to ensure coordinates are inside 'features' for the Python ST_Contains join.
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
  } catch (e) { console.error("Ensemble prediction engine failure", e); }
  return null;
}

/** 
 * Ingestion: Uploads GeoJSON boundaries to DIS.
 */
export async function uploadGeoJSON(file) {
  try {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE.DIS}/ingest/geojson`, { method: 'POST', body: formData });
    return res.ok;
  } catch (e) {
    console.error("GeoJSON ingestion network error", e);
    return false; 
  }
}

/**
 * Ingestion: Packages flat form data into the JSON-metadata structure DIS expects for Rasters.
 */
export async function uploadRaster(formData) {
  try {
    const disPayload = new FormData();
    disPayload.append('file', formData.get('file'));
    const metadata = {
      asset_type: formData.get('data_type') || 'PredictorStack',
      datetime: new Date(formData.get('date')).toISOString(),
      crop_id: "Maize"
    };
    disPayload.append('metadata', JSON.stringify(metadata));
    const res = await fetch(`${API_BASE.DIS}/ingest`, { method: 'POST', body: disPayload });
    return res.ok;
  } catch (e) { 
    console.error("Raster ingestion network error", e);
    return false; 
  }
}

/**
 * Ingestion: Uploads GEE CSVs (Ward Stats or ML Samples).
 */
export async function uploadCSV(file, type) {
  try {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE.DIS}/ingest/csv/${type}`, { method: 'POST', body: formData });
    return res.ok;
  } catch (e) { 
    console.error("Tabular ingestion network error", e);
    return false; 
  }
}

/**
 * Analytics: Fetch specific biophysical statistics for a selected county unit.
 */
 export async function fetchWardStats(wardId, year = 2024) {
  try {
    const res = await fetch(`${API_BASE.GEO}/regions/${wardId}/stats?year=${year}`);
    if (res.ok) return await res.json();
  } catch (e) {
    console.error("Unit biophysical statistics fetch error", e);
  }
  return null;
}
import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Polygon, Popup } from 'react-leaflet';
import { fetchRegions, fetchWardStats } from '../services/api';
import 'leaflet/dist/leaflet.css';

export default function FieldMap() {
  const [regions, setRegions] = useState([]);
  const [selectedUnitStats, setSelectedUnitStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const kenyaCenter = [1.0435, 34.9589];

  useEffect(() => {
    const load = async () => { 
      const data = await fetchRegions(); 
      setRegions(data); 
    };
    load();
  }, []);

  const handlePolygonClick = async (wardId) => {
    setLoading(true);
    try {
      const stats = await fetchWardStats(wardId);
      setSelectedUnitStats(stats);
    } catch (error) {
      console.error("Failed to fetch stats for unit:", wardId);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: selectedUnitStats || loading ? '1fr 380px' : '1fr', gap: '20px', transition: 'all 0.4s ease' }}>
      <div className="map-container-wrapper">
        <h3 className="section-title">🗺️ Trans Nzoia County Boundaries Map</h3>
        <div className="map-container">
          <MapContainer center={kenyaCenter} zoom={9} style={{ height: '100%', width: '100%' }}>
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
            {regions.map(r => r.geometry && (
              <Polygon
                key={r.id}
                positions={r.geometry}
                eventHandlers={{ click: () => handlePolygonClick(r.id) }}
                pathOptions={{ 
                  color: selectedUnitStats?.id === r.id ? '#fff' : '#00ff88', 
                  fillColor: '#00ff88', 
                  fillOpacity: selectedUnitStats?.id === r.id ? 0.4 : 0.2,
                  weight: selectedUnitStats?.id === r.id ? 3 : 1
                }}
              >
                <Popup>
                  <div style={{ color: '#0a0e27' }}>
                    <strong>{r.name} County Unit</strong><br />
                    Click to analyze biophysical signature.
                  </div>
                </Popup>
              </Polygon>
            ))}
          </MapContainer>
        </div>
      </div>

      {(loading || selectedUnitStats) && (
        <div className="form-container animated fadeIn" style={{ margin: 0, height: 'fit-content', border: '1px solid var(--primary)', overflowY: 'auto', maxHeight: '85vh' }}>
          {loading ? (
            <div style={{ padding: '40px', textAlign: 'center' }}>
              <div className="status-dot" style={{ margin: '0 auto 15px' }}></div>
              <p style={{ color: 'var(--primary)', fontWeight: '600' }}>Fetching GEE Zonal Stats...</p>
            </div>
          ) : (
            <>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                <h3 className="section-title" style={{ margin: 0, fontSize: '18px' }}>📊 Unit Insights</h3>
                <button onClick={() => setSelectedUnitStats(null)} style={{ background: 'none', border: 'none', color: '#fff', cursor: 'pointer', fontSize: '20px' }}>×</button>
              </div>
              
              <div style={{ marginBottom: '20px' }}>
                <h2 style={{ color: 'var(--secondary)', fontSize: '24px', fontWeight: '800' }}>{selectedUnitStats.name}</h2>
                <div className={`badge ${selectedUnitStats.status === 'Warning' ? 'bg-red' : 'bg-green'}`} style={{fontSize: '10px', marginTop: '5px'}}>
                   Status: {selectedUnitStats.status}
                </div>
              </div>

              {/* Biophysical Metrics Loop */}
              <div className="biophysical-grid" style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {Object.entries(selectedUnitStats.biophysical_signature).map(([key, data]) => (
                  <div key={key} style={{ padding: '12px', background: 'rgba(0,255,136,0.05)', borderRadius: '8px', border: '1px solid rgba(0,255,136,0.1)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
                      <span style={{ fontSize: '13px', color: 'rgba(255,255,255,0.7)', fontWeight: 'bold' }}>{key}</span>
                      {data.dev && (
                        <span className={`badge ${parseFloat(data.dev) < 0 ? 'bg-red' : 'bg-green'}`} style={{fontSize: '10px'}}>
                          {data.dev} anomaly
                        </span>
                      )}
                    </div>
                    <div style={{ fontWeight: '700', color: 'var(--primary)', fontSize: '20px' }}>{data.val}</div>
                    <div style={{ fontSize: '11px', color: 'rgba(255,255,255,0.5)', marginTop: '4px' }}>{data.desc}</div>
                  </div>
                ))}
              </div>

              {/* Explanatory Footer: Informed Decisions Support */}
              <div style={{ marginTop: '25px', padding: '15px', borderRadius: '10px', background: 'rgba(0,136,255,0.15)', border: '1px solid rgba(0,136,255,0.3)', fontSize: '12px', lineHeight: '1.6', color: '#fff' }}>
                 <p style={{ fontWeight: 'bold', color: 'var(--secondary)', marginBottom: '8px' }}>🛰️ GEE Predictor Stack Logic:</p>
                 <ul style={{ paddingLeft: '15px', margin: 0 }}>
                   <li><strong>NDVI:</strong> Multi-band proxy for vegetative health.</li>
                   <li><strong>Precipitation:</strong> Cumulative moisture from CHIRPS daily.</li>
                   <li><strong>Thermal:</strong> Integrated surface heat from ERA5-Land.</li>
                 </ul>
                 <p style={{ marginTop: '10px', fontSize: '11px', opacity: 0.8 }}>
                   Anomalies are calculated relative to a 10-year GEE baseline to support prescriptive food security decisions.
                 </p>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
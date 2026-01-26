import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Polygon, Popup, useMap } from 'react-leaflet';
import { 
  fetchRegions, 
  fetchWardStats, 
  fetchAvailableCounties, 
  fetchAvailableYears 
} from '../services/api';
import 'leaflet/dist/leaflet.css';

// Internal helper component to handle map auto-centering (FlyTo)
function MapController({ center }) {
  const map = useMap();
  useEffect(() => {
    if (center) {
      map.flyTo(center, 9, { animate: true, duration: 1.5 });
    }
  }, [center, map]);
  return null;
}

export default function FieldMap() {
  const [regions, setRegions] = useState([]);
  const [counties, setCounties] = useState([]);
  const [years, setYears] = useState([]);
  const [selectedCounty, setSelectedCounty] = useState(null);
  const [selectedYear, setSelectedYear] = useState(2024);
  const [selectedUnitStats, setSelectedUnitStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const defaultCenter = [1.0435, 34.9589];

  // Initial Discovery: Load available Counties and Years from Database
  useEffect(() => {
    const initDiscovery = async () => {
      setLoading(true);
      try {
        const [countyList, yearList] = await Promise.all([
          fetchAvailableCounties(),
          fetchAvailableYears()
        ]);

        setCounties(countyList);
        // Default years if DB is empty
        const availableYears = yearList.length > 0 ? yearList : [2024, 2023];
        setYears(availableYears);

        if (countyList.length > 0) {
          const defaultCounty = countyList[0];
          setSelectedCounty(defaultCounty);
          const defaultYear = availableYears[0];
          setSelectedYear(defaultYear);
          
          const regionData = await fetchRegions(defaultCounty.name, defaultYear);
          setRegions(regionData);
        }
      } catch (error) {
        console.error("Discovery failed:", error);
      } finally {
        setLoading(false);
      }
    };
    initDiscovery();
  }, []);

  // Handle County Switch
  const handleCountyChange = async (e) => {
    const countyName = e.target.value;
    const countyObj = counties.find(c => c.name === countyName);
    setSelectedCounty(countyObj);
    setSelectedUnitStats(null); // FIX: Clear sidebar to prevent data mismatch
    
    setLoading(true);
    try {
        const data = await fetchRegions(countyName, selectedYear);
        setRegions(data);
    } catch (err) {
        console.error("Failed to load county regions");
    } finally {
        setLoading(false);
    }
  };

  // Handle Season/Year Switch
  const handleYearChange = async (e) => {
    const year = parseInt(e.target.value);
    setSelectedYear(year);
    setSelectedUnitStats(null); // FIX: Clear sidebar to prevent temporal data mismatch
    
    setLoading(true);
    try {
        const data = await fetchRegions(selectedCounty?.name, year);
        setRegions(data);
    } catch (err) {
        console.error("Failed to load seasonal data");
    } finally {
        setLoading(false);
    }
  };

  // Handle Spatial Click (Ward stats)
  const handlePolygonClick = async (wardId) => {
    setLoading(true);
    try {
      // Pass both ID and Year to the backend for accurate temporal stats
      const stats = await fetchWardStats(wardId, selectedYear);
      setSelectedUnitStats(stats);
    } catch (error) {
      console.error("Failed to fetch stats for unit:", wardId);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="map-page-container" style={{ position: 'relative', height: '600px', width: '100%', overflow: 'hidden', borderRadius: '24px' }}>
      
      {/* 1. LAYER: THE MAP (Always Full Width to stop glitchy transitions) */}
      <div className="map-container-wrapper" style={{ height: '100%', width: '100%' }}>
        
        {/* Floating Filter Bar */}
        <div className="filter-bar" style={{ 
          position: 'absolute', top: '20px', left: '20px', zIndex: 1000, 
          display: 'flex', gap: '10px', background: 'rgba(10, 14, 39, 0.8)',
          padding: '10px', borderRadius: '12px', backdropFilter: 'blur(10px)',
          border: '1px solid rgba(0, 255, 136, 0.3)'
        }}>
          <select 
            className="form-select" 
            style={{ width: '200px', margin: 0 }} 
            onChange={handleCountyChange} 
            value={selectedCounty?.name}
          >
            {counties.length > 0 ? (
              counties.map(c => <option key={c.name} value={c.name}>{c.name} County</option>)
            ) : (
              <option>No Counties Found</option>
            )}
          </select>

          <select 
            className="form-select" 
            style={{ width: '130px', margin: 0 }} 
            onChange={handleYearChange} 
            value={selectedYear}
          >
            {years.map(y => <option key={y} value={y}>{y} Season</option>)}
          </select>
        </div>

        <MapContainer center={defaultCenter} zoom={9} style={{ height: '100%', width: '100%' }}>
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
          
          <MapController center={selectedCounty?.center} />

          {regions.map(r => r.geometry && (
            <Polygon
              key={`${r.id}-${selectedYear}`}
              positions={r.geometry}
              eventHandlers={{ click: () => handlePolygonClick(r.id) }}
              pathOptions={{ 
                color: selectedUnitStats?.id === r.id ? '#fff' : '#00ff88', 
                fillColor: '#00ff88', 
                fillOpacity: selectedUnitStats?.id === r.id ? 0.5 : 0.2,
                weight: selectedUnitStats?.id === r.id ? 3 : 1
              }}
            >
              <Popup>
                <div style={{ color: '#0a0e27' }}>
                  <strong>{r.name}</strong><br />
                  County: {r.county}<br />
                  Click to analyze {selectedYear} signature.
                </div>
              </Popup>
            </Polygon>
          ))}
        </MapContainer>
      </div>

      {/* 2. LAYER: THE OVERLAY SIDEBAR (Floats over map, no grid push) */}
      {(loading || selectedUnitStats) && (
        <div className="info-sidebar animated slideInRight" style={{ 
          position: 'absolute', right: '15px', top: '15px', bottom: '15px', 
          width: '360px', zIndex: 1001, background: 'rgba(10, 14, 39, 0.95)',
          backdropFilter: 'blur(20px)', border: '1px solid var(--primary)',
          borderRadius: '20px', padding: '25px', overflowY: 'auto',
          boxShadow: '-10px 0 40px rgba(0,0,0,0.6)'
        }}>
          {loading ? (
            <div style={{ padding: '60px 0', textAlign: 'center' }}>
              <div className="status-dot" style={{ margin: '0 auto 15px' }}></div>
              <p style={{ color: 'var(--primary)', fontWeight: '600' }}>Syncing GEE Temporal Data...</p>
            </div>
          ) : (
            <>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <h3 className="section-title" style={{ margin: 0, fontSize: '18px' }}>📊 Unit Insights</h3>
                <button 
                  onClick={() => setSelectedUnitStats(null)} 
                  style={{ background: 'rgba(255,255,255,0.1)', border: 'none', color: '#fff', cursor: 'pointer', fontSize: '20px', width: '30px', height: '30px', borderRadius: '50%' }}
                >
                  ×
                </button>
              </div>
              
              <div style={{ marginBottom: '25px' }}>
                <h2 style={{ color: 'var(--secondary)', fontSize: '26px', fontWeight: '800', marginBottom: '5px' }}>{selectedUnitStats.name}</h2>
                <div className={`badge ${selectedUnitStats.status === 'Warning' ? 'bg-red' : 'bg-green'}`} style={{ padding: '5px 12px' }}>
                   System Status: {selectedUnitStats.status}
                </div>
                <p style={{ fontSize: '12px', color: 'rgba(255,255,255,0.5)', marginTop: '10px' }}>
                   {selectedUnitStats.county} County • {selectedYear} Production Cycle
                </p>
              </div>

              {/* Biophysical Metrics */}
              <div className="biophysical-grid" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {Object.entries(selectedUnitStats.biophysical_signature).map(([key, data]) => (
                  <div key={key} style={{ padding: '14px', background: 'rgba(0,255,136,0.05)', borderRadius: '12px', border: '1px solid rgba(0,255,136,0.1)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                      <span style={{ fontSize: '13px', color: 'rgba(255,255,255,0.7)', fontWeight: 'bold' }}>{key}</span>
                      {data.dev && (
                        <span className={`badge ${parseFloat(data.dev) < 0 ? 'bg-red' : 'bg-green'}`} style={{fontSize: '10px'}}>
                          {data.dev} anomaly
                        </span>
                      )}
                    </div>
                    <div style={{ fontWeight: '700', color: 'var(--primary)', fontSize: '22px' }}>{data.val}</div>
                    <div style={{ fontSize: '11px', color: 'rgba(255,255,255,0.4)', marginTop: '5px' }}>{data.desc}</div>
                  </div>
                ))}
              </div>

              {/* DSS Support Logic Explanation */}
              <div style={{ marginTop: '30px', padding: '18px', borderRadius: '15px', background: 'rgba(0,136,255,0.15)', border: '1px solid rgba(0,136,255,0.3)', fontSize: '12px', lineHeight: '1.6', color: '#fff' }}>
                 <p style={{ fontWeight: 'bold', color: 'var(--secondary)', marginBottom: '8px' }}>🛰️ GEE Predictor Stack Logic:</p>
                 <ul style={{ paddingLeft: '15px', margin: 0, listStyleType: 'square' }}>
                   <li><strong>NDVI:</strong> Multi-band proxy for vegetative health and biomass.</li>
                   <li><strong>Precipitation:</strong> Cumulative seasonal moisture sourced from CHIRPS.</li>
                   <li><strong>Thermal:</strong> Integrated surface heat accumulation from ERA5-Land.</li>
                 </ul>
                 <p style={{ marginTop: '12px', fontSize: '11px', opacity: 0.8, fontStyle: 'italic' }}>
                   Anomalies are calculated relative to a dynamic baseline of all units within {selectedUnitStats.county} County to support localized food security decisions.
                 </p>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
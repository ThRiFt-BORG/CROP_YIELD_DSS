import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Polygon, Popup } from 'react-leaflet';
import { fetchRegions } from '../services/api';
import 'leaflet/dist/leaflet.css';

export default function FieldMap({ showNotification }) {
  const [regions, setRegions] = useState([]);

  useEffect(() => {
    loadRegions();
  }, []);

  const loadRegions = async () => {
    const data = await fetchRegions();
    setRegions(data);
  };

  return (
    <>
      <div className="map-container-wrapper">
        <h3 className="section-title">🗺️ Field Regions Map</h3>
        <div className="map-container">
          <MapContainer center={[40.7128, -74.0060]} zoom={12} style={{ height: '100%', width: '100%' }}>
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
            {regions.map(r => r.geometry && (
              <Polygon
                key={r.id}
                positions={r.geometry}
                pathOptions={{ color: '#00ff88', fillColor: '#00ff88', fillOpacity: 0.2 }}
              >
                <Popup>
                  <div style={{ color: '#0a0e27' }}>
                    <strong>{r.name}</strong><br />
                    Area: {r.area}<br />
                    Crop: {r.crop}
                  </div>
                </Popup>
              </Polygon>
            ))}
          </MapContainer>
        </div>
      </div>

      <div className="data-table-container">
        <h3 className="section-title">📍 Field Regions List</h3>
        <div className="data-table">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Area</th>
                <th>Crop</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {regions.map(r => (
                <tr key={r.id}>
                  <td>{r.id}</td>
                  <td>{r.name}</td>
                  <td>{r.area}</td>
                  <td>{r.crop}</td>
                  <td><span className="status-active">✓ Active</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
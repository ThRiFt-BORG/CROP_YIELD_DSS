import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Polygon, Popup } from 'react-leaflet';
import { fetchRegions } from '../services/api';
import 'leaflet/dist/leaflet.css';

export default function FieldMap() {
  const [regions, setRegions] = useState([]);
  const kenyaCenter = [1.0435, 34.9589];

  useEffect(() => {
    const load = async () => { const data = await fetchRegions(); setRegions(data); };
    load();
  }, []);

  return (
    <div className="map-container-wrapper">
      <h3 className="section-title">🗺️ Trans Nzoia Ward Map</h3>
      <div className="map-container">
        <MapContainer center={kenyaCenter} zoom={9} style={{ height: '100%', width: '100%' }}>
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
          {regions.map(r => r.geometry && (
            <Polygon
              key={r.id}
              positions={r.geometry}
              pathOptions={{ color: '#00ff88', fillColor: '#00ff88', fillOpacity: 0.2 }}
            >
              <Popup>
                <div style={{ color: '#0a0e27' }}>
                  <strong>{r.name} Ward</strong><br />
                  GEE Data: Available
                </div>
              </Popup>
            </Polygon>
          ))}
        </MapContainer>
      </div>
    </div>
  );
}
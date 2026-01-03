import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet';
import { useState, useCallback } from 'react';
import { useYieldStore } from '../store/yieldStore';
import { fetchYieldData } from '../services/geoApi';

const DEFAULT_CENTER: [number, number] = [34.0522, -118.2437]; // Los Angeles (Placeholder)
const DEFAULT_ZOOM = 5;

function LocationMarker() {
  const [position, setPosition] = useState<[number, number] | null>(null);
  const { setYieldData, setLoading, setError } = useYieldStore();

  const map = useMapEvents({
    click(e) {
      const { lat, lng } = e.latlng;
      setPosition([lat, lng]);
      setLoading(true);
      setError(null);

      // Hardcoded date range for demonstration
      const dateRange = { start: "2024-01-01", end: "2024-12-31" };

      fetchYieldData(lng, lat, dateRange)
        .then(data => {
          setYieldData(data);
        })
        .catch(err => {
          console.error("API Error:", err);
          setError("Failed to fetch data. Check API status.");
        })
        .finally(() => {
          setLoading(false);
        });
    },
  });

  return position === null ? null : (
    <Marker position={position} />
  );
}

export default function MapView() {
  return (
    <MapContainer 
      center={DEFAULT_CENTER} 
      zoom={DEFAULT_ZOOM} 
      scrollWheelZoom={true}
      className="h-full w-full"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <LocationMarker />
    </MapContainer>
  );
}

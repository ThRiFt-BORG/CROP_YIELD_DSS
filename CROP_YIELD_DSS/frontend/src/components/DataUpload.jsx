import React, { useState, useRef } from 'react';
import { uploadRaster, uploadCSV, uploadGeoJSON } from '../services/api'; // Added uploadGeoJSON

export default function DataUpload({ showNotification }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (selected) {
      setFile(selected);
      showNotification(`File selected: ${selected.name}`, 'info');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      showNotification('Please select a file', 'error');
      return;
    }

    setUploading(true);
    const fileName = file.name.toLowerCase();

    try {
      let success = false;
      
      if (fileName.endsWith('.geojson') || fileName.endsWith('.json')) {
        // NEW: Routing to GeoJSON Ingestion
        success = await uploadGeoJSON(file);
      } else if (fileName.endsWith('.csv')) {
        const tableType = fileName.includes('ward') ? 'wards' : 'samples';
        success = await uploadCSV(file, tableType);
      } else {
        const formData = new FormData(e.currentTarget);
        success = await uploadRaster(formData);
      }

      if (success) {
        showNotification('Data successfully ingested!', 'success');
        setFile(null);
      } else {
        showNotification('Upload failed. Check service logs.', 'error');
      }
    } catch (error) {
      showNotification('Network error during upload', 'error');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="form-container">
      <h3 className="section-title">⬆️ Data Ingestion Pipeline</h3>
      <form onSubmit={handleSubmit}>
        <div 
          className="upload-area" 
          onClick={() => fileInputRef.current.click()}
          style={{ border: file ? '3px dashed var(--primary)' : '3px dashed rgba(0, 255, 136, 0.3)' }}
        >
          <div className="upload-icon">{file ? '✅' : '🛰️'}</div>
          <div className="upload-text">{file ? file.name : 'Select GEE Stack, CSV, or GeoJSON'}</div>
          <input
            ref={fileInputRef}
            type="file"
            name="file"
            accept=".tif,.tiff,.cog,.csv,.geojson,.json" 
            className="hidden"
            style={{ display: 'none' }}
            onChange={handleFileChange}
          />
        </div>

        <div className="form-group">
          <label className="form-label">Observation Date</label>
          <input type="date" className="form-input" name="date" required />
        </div>

        <button type="submit" className="btn-primary" disabled={uploading} style={{ width: '100%' }}>
          {uploading ? 'Processing...' : '🚀 Start Ingestion'}
        </button>
      </form>
    </div>
  );
}
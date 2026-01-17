import React, { useState, useEffect } from 'react';
import { fetchRegions, uploadRaster } from '../services/api';

export default function DataUpload({ showNotification }) {
  const [regions, setRegions] = useState([]);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    loadRegions();
  }, []);

  const loadRegions = async () => {
    const data = await fetchRegions();
    setRegions(data);
  };

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    setFile(selected);
    if (selected) {
      showNotification(`File selected: ${selected.name}`, 'success');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      showNotification('Please select a file', 'error');
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('data_type', e.target.dataType.value);
    formData.append('acquisition_date', e.target.date.value);
    formData.append('region_id', e.target.region.value);
    formData.append('description', e.target.description.value);

    const success = await uploadRaster(formData);
    setUploading(false);
    
    if (success) {
      showNotification('File uploaded successfully', 'success');
      e.target.reset();
      setFile(null);
    } else {
      showNotification('Upload failed - using simulation', 'error');
    }
  };

  return (
    <>
      <div className="upload-container">
        <div className="upload-area" onClick={() => document.getElementById('fileInput').click()}>
          <div className="upload-icon">📁</div>
          <div className="upload-text">Click to Upload Raster Data</div>
          <div className="upload-hint">Supports GeoTIFF, COG formats • Max 500MB</div>
          <input
            id="fileInput"
            type="file"
            accept=".tif,.tiff,.cog"
            style={{ display: 'none' }}
            onChange={handleFileChange}
          />
        </div>
      </div>

      <div className="form-container">
        <h3 className="section-title">📝 Upload Details</h3>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Data Type</label>
            <select className="form-select" name="dataType" required>
              <option value="">Select type...</option>
              <option value="ndvi">NDVI</option>
              <option value="precipitation">Precipitation</option>
              <option value="temperature">Temperature</option>
              <option value="soil_moisture">Soil Moisture</option>
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Acquisition Date</label>
            <input type="date" className="form-input" name="date" required />
          </div>
          <div className="form-group">
            <label className="form-label">Region (Optional)</label>
            <select className="form-select" name="region">
              <option value="">Select region...</option>
              {regions.map(r => <option key={r.id} value={r.id}>{r.name}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Description</label>
            <textarea className="form-input" name="description" rows="3" placeholder="Brief description..."></textarea>
          </div>
          <button type="submit" className="btn-primary" disabled={uploading}>
            <span>⬆️</span>
            <span>{uploading ? 'Uploading...' : 'Process & Upload'}</span>
          </button>
        </form>
      </div>
    </>
  );
}
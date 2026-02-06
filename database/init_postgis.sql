-- Initialize PostgreSQL database with PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- 1. Region Table (General administrative reference)
CREATE TABLE IF NOT EXISTS region (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    geom GEOMETRY(MULTIPOLYGON, 4326)
);

-- 2. YieldObservation Table (ML Samples & Historical Ground Truth)
-- Updated with 'county_name' for national-scale traceability
CREATE TABLE IF NOT EXISTS yieldobservation (
    id SERIAL PRIMARY KEY,
    crop_id VARCHAR(50) NOT NULL DEFAULT 'Maize',
    county_name VARCHAR(100), -- NEW: Supports 47-county filtering
    year INTEGER NOT NULL,
    yield_value FLOAT NOT NULL,
    ndvi_mean FLOAT,
    precip_mean FLOAT,
    et_mean FLOAT,
    temp_mean FLOAT,
    elevation FLOAT,
    soil_texture FLOAT,
    geom GEOMETRY(POINT, 4326)
);

-- 3. RasterAsset Table (Metadata for GEE Multi-band Tiff Stacks)
CREATE TABLE IF NOT EXISTS rasterasset (
    id SERIAL PRIMARY KEY,
    asset_url VARCHAR(512) NOT NULL,
    datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    asset_type VARCHAR(50) NOT NULL,
    bands JSON, 
    bbox GEOMETRY(POLYGON, 4326)
);

-- 4. AuxiliaryData Table (GEE Zonal Statistics per County Unit)
-- RECALIBRATED: Added county_name and year for dynamic discovery logic
CREATE TABLE IF NOT EXISTS auxiliarydata (
    id SERIAL PRIMARY KEY,
    ward_name VARCHAR(100) NOT NULL,
    ward_id VARCHAR(50),
    county_name VARCHAR(100) NOT NULL, -- NEW: Enables /counties dropdown
    year INTEGER NOT NULL,             -- NEW: Enables /years temporal filter
    ndvi_mean FLOAT,
    precip_mean FLOAT,
    et_mean FLOAT,
    temp_mean FLOAT,
    elevation_m FLOAT,
    soil_texture FLOAT,
    geom GEOMETRY(MULTIPOLYGON, 4326) 
);

-- Create Spatial and Functional Indexes
CREATE INDEX IF NOT EXISTS region_geom_idx ON region USING GIST (geom);
CREATE INDEX IF NOT EXISTS yieldobservation_geom_idx ON yieldobservation USING GIST (geom);
CREATE INDEX IF NOT EXISTS rasterasset_geom_idx ON rasterasset USING GIST (bbox);
CREATE INDEX IF NOT EXISTS auxiliarydata_geom_idx ON auxiliarydata USING GIST (geom);

-- NEW: B-Tree Indexes for high-speed filtering in the 47-county system
CREATE INDEX IF NOT EXISTS idx_auxiliary_county ON auxiliarydata (county_name);
CREATE INDEX IF NOT EXISTS idx_auxiliary_year ON auxiliarydata (year);
CREATE INDEX IF NOT EXISTS idx_yield_year ON yieldobservation (year);
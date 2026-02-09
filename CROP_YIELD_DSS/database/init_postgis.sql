-- Initialize PostgreSQL database with PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- 1. Region Table (General administrative reference)
CREATE TABLE IF NOT EXISTS region (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    geom GEOMETRY(MULTIPOLYGON, 4326)
);

-- 2. YieldObservation Table (ML Samples & Historical Ground Truth)
-- RECALIBRATED: Added Ensemble Breakdown and GDD columns
CREATE TABLE IF NOT EXISTS yieldobservation (
    id SERIAL PRIMARY KEY,
    crop_id VARCHAR(50) NOT NULL DEFAULT 'Maize',
    county_name VARCHAR(100), 
    year INTEGER NOT NULL,
    yield_value FLOAT NOT NULL,
    -- ENSEMBLE TRACEABILITY COLUMNS
    rf_contribution FLOAT,        -- NEW: Statistical result
    dssat_contribution FLOAT,     -- NEW: Mechanistic result
    limiting_factor VARCHAR(100), -- NEW: e.g., 'Thermal Stress'
    -- BIOPHYSICAL FEATURES
    ndvi_mean FLOAT,
    evi_mean FLOAT,               -- NEW: Enhanced Vegetation Index
    precip_sum FLOAT,
    gdd_total FLOAT,              -- NEW: Growing Degree Days
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
-- RECALIBRATED: Added Heat Sum and 2020 Baseline
CREATE TABLE IF NOT EXISTS auxiliarydata (
    id SERIAL PRIMARY KEY,
    ward_name VARCHAR(100) NOT NULL,
    ward_id VARCHAR(50),
    county_name VARCHAR(100) NOT NULL,
    year INTEGER NOT NULL,             
    ndvi_mean FLOAT,
    precip_sum FLOAT,
    et_mean FLOAT,
    temp_mean FLOAT,
    gdd_total FLOAT,        -- NEW: Accumulated heat per ward
    yield_2020 FLOAT,       -- NEW: SPAM 2020 Baseline for Gap Analysis
    elevation_m FLOAT,
    soil_texture FLOAT,
    geom GEOMETRY(MULTIPOLYGON, 4326) 
);

-- Create Spatial and Functional Indexes
CREATE INDEX IF NOT EXISTS region_geom_idx ON region USING GIST (geom);
CREATE INDEX IF NOT EXISTS yieldobservation_geom_idx ON yieldobservation USING GIST (geom);
CREATE INDEX IF NOT EXISTS rasterasset_geom_idx ON rasterasset USING GIST (bbox);
CREATE INDEX IF NOT EXISTS auxiliarydata_geom_idx ON auxiliarydata USING GIST (geom);

-- B-Tree Indexes for high-speed filtering
CREATE INDEX IF NOT EXISTS idx_auxiliary_county ON auxiliarydata (county_name);
CREATE INDEX IF NOT EXISTS idx_auxiliary_year ON auxiliarydata (year);
CREATE INDEX IF NOT EXISTS idx_yield_year ON yieldobservation (year);
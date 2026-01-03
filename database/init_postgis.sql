-- Initialize PostgreSQL database with PostGIS extension

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- 1. Region Table (for administrative or field boundaries)
CREATE TABLE IF NOT EXISTS region (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    -- MULTIPOLYGON for complex boundaries
    geom GEOMETRY(MULTIPOLYGON, 4326)
);
-- Create spatial index
CREATE INDEX region_geom_idx ON region USING GIST (geom);

-- 2. YieldObservation Table (Ground Truth & Tabular Records)
CREATE TABLE IF NOT EXISTS yieldobservation (
    id SERIAL PRIMARY KEY,
    crop_id VARCHAR(50) NOT NULL,
    year INTEGER NOT NULL,
    yield_value FLOAT NOT NULL,
    planting_date DATE,
    harvest_date DATE,
    -- POINT for specific observation location
    geom GEOMETRY(POINT, 4326)
);
-- Create spatial index
CREATE INDEX yieldobservation_geom_idx ON yieldobservation USING GIST (geom);

-- 3. RasterAsset Table (Metadata for Remote Sensing Data - STAC-like)
CREATE TABLE IF NOT EXISTS rasterasset (
    id SERIAL PRIMARY KEY,
    asset_url VARCHAR(512) NOT NULL,
    datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    asset_type VARCHAR(50) NOT NULL, -- e.g., 'Sentinel-2', 'NDVI'
    -- BBOX geometry for spatial indexing
    bbox GEOMETRY(POLYGON, 4326)
);
-- Create spatial index
CREATE INDEX rasterasset_geom_idx ON rasterasset USING GIST (bbox);

-- 4. AuxiliaryData Table (Soil, Terrain, etc.)
CREATE TABLE IF NOT EXISTS auxiliarydata (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) NOT NULL,
    value FLOAT,
    -- Generic GEOMETRY for various spatial types
    geom GEOMETRY(GEOMETRY, 4326)
);
-- Create spatial index
CREATE INDEX auxiliarydata_geom_idx ON auxiliarydata USING GIST (geom);

-- Sample data for testing only.

-- Insert placeholder data for Region (a simple square)
INSERT INTO region (name, geom) VALUES
('Sample Field A', ST_GeomFromText('MULTIPOLYGON(((0 0, 0 10, 10 10, 10 0, 0 0)))', 4326)),
('Sample Field B', ST_GeomFromText('MULTIPOLYGON(((15 15, 15 25, 25 25, 25 15, 15 15)))', 4326));

-- Insert placeholder data for YieldObservation
INSERT INTO yieldobservation (crop_id, year, yield_value, geom) VALUES
('corn', 2024, 150.5, ST_GeomFromText('POINT(5 5)', 4326)),
('soybean', 2024, 55.2, ST_GeomFromText('POINT(8 2)', 4326)),
('corn', 2024, 180.0, ST_GeomFromText('POINT(20 20)', 4326));

-- Insert placeholder data for RasterAsset
INSERT INTO rasterasset (asset_url, datetime, asset_type, bbox) VALUES
('s3://dss-cogs/S2_20240601.tif', '2024-06-01 10:00:00Z', 'Sentinel-2', ST_GeomFromText('POLYGON((0 0, 0 10, 10 10, 10 0, 0 0))', 4326)),
('s3://dss-cogs/ERA5_20240601.tif', '2024-06-01 12:00:00Z', 'ERA5', ST_GeomFromText('POLYGON((15 15, 15 25, 25 25, 25 15, 15 15))', 4326));

-- Insert placeholder data for AuxiliaryData
INSERT INTO auxiliarydata (key, value, geom) VALUES
('soil_type', 1.0, ST_GeomFromText('POLYGON((0 0, 0 10, 10 10, 10 0, 0 0))', 4326)),
('elevation', 100.0, ST_GeomFromText('POINT(5 5)', 4326));

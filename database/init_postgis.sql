CREATE EXTENSION IF NOT EXISTS postgis;

-- 1. Region Table
CREATE TABLE IF NOT EXISTS region (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    geom GEOMETRY(MULTIPOLYGON, 4326)
);

-- 2. YieldObservation Table (ML Samples)
CREATE TABLE IF NOT EXISTS yieldobservation (
    id SERIAL PRIMARY KEY,
    crop_id VARCHAR(50) NOT NULL DEFAULT 'Maize',
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

-- 3. RasterAsset Table (GEE Rasters)
CREATE TABLE IF NOT EXISTS rasterasset (
    id SERIAL PRIMARY KEY,
    asset_url VARCHAR(512) NOT NULL,
    datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    asset_type VARCHAR(50) NOT NULL,
    bands JSON, -- Matches your models.py
    bbox GEOMETRY(POLYGON, 4326)
);

-- 4. AuxiliaryData Table (GEE Ward Stats)
CREATE TABLE IF NOT EXISTS auxiliarydata (
    id SERIAL PRIMARY KEY,
    ward_name VARCHAR(100),
    ward_id VARCHAR(50),
    ndvi_mean FLOAT,
    precip_mean FLOAT,
    et_mean FLOAT,
    temp_mean FLOAT,
    elevation_m FLOAT,
    soil_texture FLOAT,
    geom GEOMETRY(MULTIPOLYGON, 4326) -- Matches your models.py
);

-- Create Indexes
CREATE INDEX IF NOT EXISTS region_geom_idx ON region USING GIST (geom);
CREATE INDEX IF NOT EXISTS yieldobservation_geom_idx ON yieldobservation USING GIST (geom);
CREATE INDEX IF NOT EXISTS rasterasset_geom_idx ON rasterasset USING GIST (bbox);
CREATE INDEX IF NOT EXISTS auxiliarydata_geom_idx ON auxiliarydata USING GIST (geom);
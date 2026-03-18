# Kenya National Crop Yield DSS

## Overview

A national-scale agricultural data pipeline and Decision Support System (DSS) for crop yield forecasting across Kenya.

This system standardizes heterogeneous geospatial datasets and integrates:

- Machine Learning (Random Forest)
- Mechanistic Crop Modeling (DSSAT)

Goal: Transform raw agricultural data into standardized, analysis-ready datasets aligned with workflows like Carob.

---

## Core Data Pipeline

```
Google Earth Engine (Sentinel-2, CHIRPS, ERA5)
        ↓
Data Ingestion Service (DIS)
        ↓
COG + JSON Metadata (Standardized)
        ↓
PostGIS Database
        ↓
Hybrid Modeling (Random Forest + DSSAT)
        ↓
Yield Predictions (County Level)
```

---

## Key Features

### 1. Data Standardization (Carob-Aligned)

- Converts raw GeoTIFFs → Cloud Optimized GeoTIFFs (COGs)
- Generates structured metadata (JSON/GeoJSON)
- Applies ISO 19157 data quality principles
- Ensures reproducible, consistent datasets

### 2. Automated Data Ingestion

- GEE integration (Sentinel-2, CHIRPS, ERA5)
- Raster preprocessing + validation
- Dataset cataloging into PostGIS

### 3. Hybrid Agricultural Modeling

- Random Forest → captures statistical patterns
- DSSAT → simulates biological crop processes
- Combined output → robust yield predictions

### 4. Reproducible Architecture

- Dockerized microservices
- Version-controlled workflows (Git)
- Scalable to national datasets

---

## System Architecture

```
[ Frontend (React) ]
        ↓
[ Geo API ] -----> [ PostGIS ]
        ↓
[ ML API ] -----> [ DSSAT Engine ]
        ↓
[ DIS Service ] --> [ MinIO Storage ]
```

---

## Tech Stack

- Python (FastAPI)
- PostgreSQL / PostGIS
- Google Earth Engine
- Docker / Docker Compose
- DSSAT (Fortran-based crop model)
- JavaScript (React)

---

## Project Structure

```
CROP_YIELD_DSS/
├── frontend_app/        # UI (React)
├── geo_api/             # Spatial queries (PostGIS)
├── ml_api/              # ML + DSSAT modeling
├── dis_service/         # Data ingestion & standardization
├── dss_postgres/        # Database config
├── minio_s3/            # Raster storage
├── docker-compose.yml
```

---

## Example Workflow

1. Extract datasets from Google Earth Engine
2. Process using DIS → convert to COG + metadata
3. Store in PostGIS + object storage
4. Run hybrid model (RF + DSSAT)
5. Generate yield predictions per county

---

## Data Sources

- Sentinel-2 → Vegetation indices (NDVI, EVI)
- CHIRPS → Rainfall
- ERA5 → Temperature / GDD
- SRTM → Elevation
- SPAM 2020 → Baseline yield

---

## Model Performance

- R²: 0.79
- Validation: Grouped K-Fold (county level)

---

## Setup (Minimal)

```bash
docker compose up -d --build
```

---

## Outputs

- County-level yield predictions
- Processed raster datasets (COG)
- Structured agricultural datasets (PostGIS)

---

## Why This Matters

Most agricultural datasets are:

- fragmented
- inconsistent
- hard to reuse

This system:

- standardizes them
- makes them reproducible
- enables scalable agricultural analysis

---

## Work in Progress

- R-based data standardization scripts
- Multi-crop modeling
- Real-time data ingestion

---

## Sample Output

Samples are pending upload as this an entirely localized system.

---

## Author

Kimani Ndungu\
Geospatial Data Scientist

---

## Repository

[https://github.com/ThRiFt-BORG/CROP\_YIELD\_DSS](https://github.com/ThRiFt-BORG/CROP_YIELD_DSS)


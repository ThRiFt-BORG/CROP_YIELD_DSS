# Geospatial Crop Yield Decision Support System (DSS)

This project implements a microservices-based architecture for crop yield modeling and visualization, leveraging modern geospatial and machine learning technologies.

## Architecture Overview

The system is a monorepo containing four microservices and a React frontend, orchestrated by Docker Compose:

1.  **geo_api**: Python FastAPI service for geospatial queries, feature extraction, and ML orchestration.
2.  **ml_api**: Python FastAPI service for yield prediction inference.
3.  **DIS (Data Ingestion Service)**: Python FastAPI service for raster processing (COG conversion) and cataloging.
4.  **Frontend**: React/TypeScript application for visualization and user interaction.
5.  **Database**: MySQL 8.0+ (with spatial support) for all application and metadata storage.
6.  **Storage**: Minio (S3-compatible) for storing Cloud Optimized GeoTIFF (COG) files.

## Local Development Setup (Docker Compose)

### Prerequisites

*   Docker and Docker Compose installed.

### 1. Clone the Repository

```bash
git clone [repository-url]
cd [repository-name]
```

### 2. Build and Run Services

The `docker-compose.yml` file will build all services and start the MySQL and Minio containers.

```bash
docker-compose up --build
```

This command performs the following:
*   Builds the Python services (geo_api, ml_api, DIS) with necessary geospatial libraries (GDAL, GEOS).
*   Starts the MySQL container, which runs `database/init_mysql.sql` to create tables and insert sample data.
*   Starts the Minio container for S3 simulation.
*   Starts the Frontend development server.

### 3. Access the Application

*   **Frontend**: Access the application in your browser at `http://localhost:3000`
*   **geo_api Docs**: `http://localhost:8000/docs`
*   **ml_api Docs**: `http://localhost:8001/docs`
*   **DIS Docs**: `http://localhost:8002/docs`
*   **Minio Console**: `http://localhost:9001` (User: `minio_user`, Pass: `minio_password`)

## Sample Data for Local Testing

To enable local testing without real datasets, sample data is inserted in `database/init_mysql.sql` for the following tables:

*   **`region`**: Contains dummy field boundaries (simple polygons).
*   **`yieldobservation`**: Contains fictional yield values at specific points for ML training simulation.
*   **`rasterasset`**: Contains placeholder metadata with fictional S3 URLs (e.g., `s3://dss-cogs/sample_cog.tif`) that point to the Minio service.
*   **`auxiliarydata`**: Contains sample elevation and soil type values for feature extraction.

**NOTE**: This sample data is for local development and testing only. For production use, these tables must be populated with real-world data.

## Database Schemas Provided

The project provides two database initialization scripts:

*   `database/init_mysql.sql`: Used for the actual implementation, leveraging MySQL's spatial functions (`ST_Contains`, `ST_PointFromText`).
*   `database/init_postgis.sql`: Provided as a reference for the original design, leveraging PostgreSQL/PostGIS spatial types and functions.

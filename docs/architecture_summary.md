# Geospatial Crop Yield DSS: Architecture Summary

## Core Design Principle

The system follows a **Microservices Architecture** pattern, where specialized functions (Geospatial Query, Machine Learning Inference, Data Ingestion) are decoupled into independent services. This design promotes scalability, maintainability, and technology independence.

## Key Architectural Decisions

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **Database** | **MySQL 8.0+ (Spatial)** | Chosen for deployment flexibility where PostGIS is unavailable. MySQL's native spatial functions (`ST_Contains`, `ST_Intersects`) are used to maintain geospatial integrity. |
| **Backend** | **Python FastAPI** | High performance, asynchronous capabilities, and a mature ecosystem for geospatial libraries (`rasterio`, `geopandas`). |
| **Containerization** | **Docker Compose** | Enables a reproducible development environment, bundling services with their exact dependencies (including GDAL/GEOS system libraries). |
| **Storage** | **Minio (S3-compatible)** | Simulates cloud object storage for Cloud Optimized GeoTIFFs (COGs), allowing the geo_api to stream data efficiently. |

## Data Flow for Yield Prediction (`/v1/query/point`)

1.  **Frontend Click**: User clicks a point on the map, sending `(lon, lat, date_range)` to the **geo_api**.
2.  **Feature Extraction (geo_api)**:
    *   Queries **MySQL** using spatial functions to retrieve auxiliary data (e.g., elevation, soil type) and raster metadata (`rasterasset`).
    *   Uses `rio-tiler` to simulate the extraction of time-series features (e.g., mean NDVI) from COG assets stored in **Minio**.
3.  **Orchestration (geo_api)**: Compiles all features into a single JSON payload.
4.  **Inference Call**: geo_api makes an internal HTTP request to the **ml_api**'s `/v1/predict` endpoint.
5.  **Prediction (ml_api)**: Loads the pre-trained `scikit-learn` model and returns the `predicted_yield`.
6.  **Response**: geo_api combines the predicted yield, features, and time-series data, returning the final `QueryPointResponse` to the **Frontend**.

## Data Ingestion Flow (DIS)

1.  **File Upload**: User uploads a raw GeoTIFF and metadata to the **DIS**.
2.  **Processing**: DIS uses `rasterio` to convert the raw GeoTIFF into a **Cloud Optimized GeoTIFF (COG)**.
3.  **Storage**: DIS uploads the COG to the **Minio** object storage.
4.  **Cataloging**: DIS extracts the bounding box and metadata, then inserts a new record into the **MySQL** `rasterasset` table, making the new data discoverable by the geo_api.

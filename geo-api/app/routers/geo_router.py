from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from shared.database.base import get_db
from shared.models.api_models import QueryPointRequest, QueryPointResponse, Feature
from geo_api.app.utils.db_utils import get_yield_observations_near_point, get_auxiliary_data_at_point, get_raster_assets_by_bbox
from geo_api.app.utils.geospatial import extract_time_series_from_cogs, call_ml_api
from typing import List

router = APIRouter()

@router.post("/query/point", response_model=QueryPointResponse)
def query_point(request: QueryPointRequest, db: Session = Depends(get_db)):
    """
    Main endpoint to query a point, extract features, call the ML-API, and return results.
    """
    point = request.point
    date_range = request.date_range
    
    # 1. Feature Extraction from Database (MySQL Spatial Queries)
    
    # Get auxiliary data (e.g., soil type, elevation)
    aux_data = get_auxiliary_data_at_point(db, point)
    
    # Compile features for ML model
    features: List[Feature] = []
    
    # Mock feature compilation based on auxiliary data
    elevation = next((d.value_data for d in aux_data if d.key_name == 'elevation'), 150.0)
    soil_type = next((d.value_data for d in aux_data if d.key_name == 'soil_type'), 2.0)
    
    features.append(Feature(name="elevation", value=elevation))
    features.append(Feature(name="soil_type", value=soil_type))
    
    # 2. Time Series Extraction (Simulated COG Access)
    
    # Get raster assets intersecting the point within the date range
    raster_assets = get_raster_assets_by_bbox(db, point, date_range)
    
    # Extract time series (simulated NDVI calculation)
    time_series = extract_time_series_from_cogs(point, raster_assets)
    
    # Add time series features to the ML feature set (e.g., mean NDVI)
    ndvi_mean = sum(ts.value for ts in time_series) / len(time_series) if time_series else 0.5
    
    features.append(Feature(name="ndvi_mean", value=ndvi_mean))
    features.append(Feature(name="temp_avg", value=25.0)) # Mock temp avg
    
    # Prepare features for ML-API call
    ml_features = {f.name: f.value for f in features}
    
    # 3. ML Prediction Orchestration
    
    predicted_yield = call_ml_api(ml_features)
    
    # 4. Return compiled response
    
    return QueryPointResponse(
        predicted_yield=predicted_yield,
        features=features,
        time_series=time_series
    )

@router.get("/assets")
def list_assets(db: Session = Depends(get_db)):
    """List all raster assets (STAC-like catalog)."""
    return db.query(RasterAsset).all()

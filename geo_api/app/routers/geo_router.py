from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Any, Dict
from datetime import datetime
import logging

# Internal shared imports
from shared.database.base import get_db
from shared.models.api_models import QueryPointRequest, QueryPointResponse, Feature, TimeSeriesData

# App-specific imports
# Note: Using 'app' prefix as geo_api/ is the root in the container
from app.utils.db_utils import get_auxiliary_data_at_point, get_raster_assets_by_bbox
from app.utils.geospatial import extract_features_from_stack, call_ml_api

# Set up logging
logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/regions")
def get_regions():
    """
    Returns the target region (Trans Nzoia) for the map and dropdowns.
    Matches the coordinates used in GEE.
    """
    return [
        {
            "id": "trans_nzoia",
            "name": "Trans Nzoia County",
            "area": "2,499 km²",
            "crop": "Maize",
            "geometry": [
                [1.2, 34.7], [1.2, 35.2], [0.8, 35.2], [0.8, 34.7], [1.2, 34.7]
            ]
        }
    ]


@router.post("/query/point", response_model=QueryPointResponse)
def query_point(request: QueryPointRequest, db: Session = Depends(get_db)):
    """
    Queries a specific geographic point, extracts features from a COG stack (from GEE),
    and calls the ML API to predict yield.
    """
    point = request.point
    
    # FIX 1: Convert Pydantic model to dict for SQLAlchemy utilities
    # Handles Pydantic v1 (dict) and v2 (model_dump)
    if hasattr(request.date_range, "model_dump"):
        date_range_dict = request.date_range.model_dump()
    else:
        date_range_dict = request.date_range.dict()
    
    # FIX 2: Explicitly type hint the list to avoid Pylance 'Unknown' errors
    assets: List[Any] = get_raster_assets_by_bbox(db, point, date_range_dict)
    
    # FIX 3: Robustly find the PredictorStack asset
    # Casting a.asset_type to str avoids SQLAlchemy 'ColumnElement' comparison errors
    stack_asset = next((a for a in assets if str(a.asset_type) == 'PredictorStack'), None)
    
    features_dict: Dict[str, float] = {}
    
    if stack_asset:
        try:
            # FIX 4: Convert SQLAlchemy Column to string for the extractor
            asset_url = str(stack_asset.asset_url)
            features_dict = extract_features_from_stack(point, asset_url)
            
            # FIX 5: Handle the list returned by get_auxiliary_data_at_point
            aux_results = get_auxiliary_data_at_point(db, point)
            if aux_results and len(aux_results) > 0:
                # Grab the first object in the list
                aux_data = aux_results[0]
                features_dict.update({
                    'soil_texture': float(getattr(aux_data, 'soil_texture', 0.0)), 
                    'elevation_mean': float(getattr(aux_data, 'elevation_m', 0.0))
                })
        except Exception as e:
            logger.error(f"Error extracting features from stack: {e}")
            raise HTTPException(status_code=500, detail="Spatial feature extraction failed")
    else:
        # Fallback values for testing/missing data
        logger.warning(f"No PredictorStack found for point {point}. Using fallbacks.")
        features_dict = {
            "ndvi_mean": 0.52, 
            "precip_mean": 5.1, 
            "et_mean": 3.8, 
            "elevation_mean": 1850.0, 
            "soil_texture": 2.0, 
            "temp_mean": 21.5
        }

    # Transform dict to Feature list for API response, ensuring float conversion
    features_list = [
        Feature(name=str(k), value=float(v)) 
        for k, v in features_dict.items()
    ]
    
    # Call ML API for yield prediction
    try:
        predicted_yield = call_ml_api(features_dict)
    except Exception as e:
        logger.error(f"ML API call failed: {e}")
        predicted_yield = 0.0 # Safety fallback

    # FIX 6: Robust Datetime Handling
    ts_date = datetime(2024, 1, 1) # Default fallback
    if stack_asset and hasattr(stack_asset, "datetime"):
        raw_dt = stack_asset.datetime
        if isinstance(raw_dt, datetime):
            ts_date = raw_dt
        elif isinstance(raw_dt, str):
            try:
                ts_date = datetime.fromisoformat(raw_dt)
            except ValueError:
                logger.warning(f"Invalid date format in asset: {raw_dt}")

    # Build TimeSeries data (currently uses NDVI as a proxy)
    time_series = [
        TimeSeriesData(
            date=ts_date, 
            value=float(features_dict.get("ndvi_mean", 0.0))
        )
    ]
    
    return QueryPointResponse(
        predicted_yield=float(predicted_yield), 
        features=features_list, 
        time_series=time_series
    )


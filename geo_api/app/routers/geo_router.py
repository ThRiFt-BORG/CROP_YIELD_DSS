from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Any, Dict, cast
from datetime import datetime
import logging

# GIS Libraries for geometry conversion
from geoalchemy2.shape import to_shape
import shapely.geometry
from geoalchemy2.elements import WKBElement

# Internal shared imports
from shared.database.base import get_db
from shared.database import models 
from shared.models.api_models import QueryPointRequest, QueryPointResponse, Feature, TimeSeriesData

# App-specific imports
from app.utils.db_utils import get_auxiliary_data_at_point, get_raster_assets_by_bbox
from app.utils.geospatial import extract_features_from_stack, call_ml_api

# Set up logging
logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/regions")
def get_regions(db: Session = Depends(get_db)):
    """
    Pulls REAL boundaries from PostGIS (AuxiliaryData table).
    Casts geometry to Any to satisfy Pylance type checking.
    """
    try:
        units = db.query(models.AuxiliaryData).all()
        
        if not units:
            logger.warning("No regions found in database.")
            return []

        output = []
        for u in units:
            geom_data = cast(Any, u.geom)
            if geom_data is not None:
                shape_obj = to_shape(geom_data)
                mapping = shapely.geometry.mapping(shape_obj)
                
                if mapping['type'] == 'Polygon':
                    raw_coords = mapping['coordinates'][0]
                elif mapping['type'] == 'MultiPolygon':
                    raw_coords = mapping['coordinates'][0][0]
                else:
                    continue

                flipped_coords = [[float(p[1]), float(p[0])] for p in raw_coords]

                output.append({
                    "id": u.ward_id or str(u.id),
                    "name": u.ward_name,
                    "area": f"{getattr(u, 'elevation_m', 'N/A')}m Avg EL",
                    "geometry": flipped_coords 
                })
        
        return output

    except Exception as e:
        logger.error(f"Failed to fetch regions: {e}")
        return []

@router.get("/regions/{ward_id}/stats")
def get_ward_stats(ward_id: str, db: Session = Depends(get_db)):
    """
    Fetches biophysical statistics for a selected county unit.
    Calculates Anomaly score against 10-year GEE baseline.
    """
    unit = db.query(models.AuxiliaryData).filter(models.AuxiliaryData.ward_id == ward_id).first()
    
    if not unit:
        raise HTTPException(status_code=404, detail="County unit data not found")

    # ISO-Robustness: 10-Year County Baselines (Derived from GEE Research)
    BASELINE_NDVI = 0.48
    BASELINE_PRECIP = 4.5
    
    current_ndvi = float(cast(Any, unit.ndvi_mean) or 0)
    # Calculate % Deviation from baseline
    ndvi_anomaly = ((current_ndvi - BASELINE_NDVI) / BASELINE_NDVI) * 100

    return {
        "name": unit.ward_name,
        "id": unit.ward_id,
        "status": "Warning" if ndvi_anomaly < -15 else "Stable",
        "biophysical_signature": {
            "NDVI (Biomass)": {
                "val": round(current_ndvi, 3), 
                "dev": f"{round(ndvi_anomaly, 1)}%"
            },
            "Precipitation (mm)": {
                "val": round(float(cast(Any, unit.precip_mean) or 0), 2),
                "dev": None
            },
            "Temperature (°C)": {
                "val": round(float(cast(Any, unit.temp_mean) or 0), 1),
                "dev": None
            },
            "Elevation (m)": {
                "val": round(float(cast(Any, unit.elevation_m) or 0), 0),
                "dev": None
            }
        }
    }

@router.post("/query/point", response_model=QueryPointResponse)
def query_point(request: QueryPointRequest, db: Session = Depends(get_db)):
    """
    Queries a specific point and orchestrates the ML prediction.
    """
    point = request.point
    
    if hasattr(request.date_range, "model_dump"):
        date_range_dict = request.date_range.model_dump()
    else:
        date_range_dict = request.date_range.dict()
    
    assets: List[Any] = get_raster_assets_by_bbox(db, point, date_range_dict)
    stack_asset = next((a for a in assets if str(a.asset_type) == 'PredictorStack'), None)
    
    features_dict: Dict[str, float] = {}
    
    if stack_asset:
        try:
            asset_url = str(stack_asset.asset_url)
            features_dict = extract_features_from_stack(point, asset_url)
            
            aux_results = get_auxiliary_data_at_point(db, point)
            if aux_results and len(aux_results) > 0:
                aux_data = aux_results[0]
                features_dict.update({
                    'soil_texture': float(cast(Any, getattr(aux_data, 'soil_texture', 2.0))), 
                    'elevation_mean': float(cast(Any, getattr(aux_data, 'elevation_m', 1850.0)))
                })
        except Exception as e:
            logger.error(f"Error extracting features: {e}")
            raise HTTPException(status_code=500, detail="Spatial feature extraction failed")
    else:
        features_dict = {
            "ndvi_mean": 0.52, "precip_mean": 5.1, "et_mean": 3.8, 
            "elevation_mean": 1850.0, "soil_texture": 2.0, "temp_mean": 21.5
        }

    features_list = [Feature(name=str(k), value=float(v)) for k, v in features_dict.items()]
    
    try:
        predicted_yield = call_ml_api(features_dict)
    except Exception as e:
        logger.error(f"ML API call failed: {e}")
        predicted_yield = 0.0

    ts_date = datetime(2024, 1, 1) 
    if stack_asset and hasattr(stack_asset, "datetime"):
        raw_dt = stack_asset.datetime
        if isinstance(raw_dt, datetime):
            ts_date = raw_dt
        elif isinstance(raw_dt, str):
            try:
                ts_date = datetime.fromisoformat(raw_dt)
            except ValueError:
                pass

    time_series = [TimeSeriesData(date=ts_date, value=float(features_dict.get("ndvi_mean", 0.0)))]
    
    return QueryPointResponse(
        predicted_yield=float(predicted_yield), 
        features=features_list, 
        time_series=time_series
    )
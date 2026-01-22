from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Column, Integer
from typing import List, Optional, Any, Dict
from datetime import datetime
import logging

# GIS Libraries for geometry conversion
from geoalchemy2.shape import to_shape
import shapely.geometry
from geoalchemy2.elements import WKBElement
from geoalchemy2 import Geometry

# Internal shared imports
from shared.database.base import get_db, Base
from shared.database import models # Added to access AuxiliaryData table
from shared.models.api_models import QueryPointRequest, QueryPointResponse, Feature, TimeSeriesData

# App-specific imports
from app.utils.db_utils import get_auxiliary_data_at_point, get_raster_assets_by_bbox
from app.utils.geospatial import extract_features_from_stack, call_ml_api

# Set up logging
logger = logging.getLogger(__name__)
router = APIRouter()

class Unit(Base):
    __tablename__ = 'units'
    id = Column(Integer, primary_key=True)
    geom = Column(Geometry('POLYGON'))  # Define the geometry type explicitly

@router.get("/regions")
def get_regions(db: Session = Depends(get_db)):
    """
    RECALIBRATED: Pulls REAL boundaries from PostGIS (AuxiliaryData table)
    instead of the hardcoded mock box.
    """
    try:
        # Query the county units/wards you uploaded via GeoJSON/CSV
        units = db.query(models.AuxiliaryData).all()
        
        if not units:
            logger.warning("No regions found in database. Map will be empty.")
            return []

        output = []
        for u in units:
            if isinstance(u.geom, WKBElement):  # Ensure the geometry is of the correct type
                # Convert PostGIS binary to Shapely object
                shape_obj = to_shape(u.geom)
                # Convert to GeoJSON-style dictionary
                mapping = shapely.geometry.mapping(shape_obj)
                
                # Handle nesting (Polygon vs MultiPolygon)
                if mapping['type'] == 'Polygon':
                    raw_coords = mapping['coordinates'][0]
                elif mapping['type'] == 'MultiPolygon':
                    # Get the exterior ring of the first polygon in the multi-collection
                    raw_coords = mapping['coordinates'][0][0]
                else:
                    continue

                # 4. Flip coordinates for Leaflet compatibility
                flipped_coords = [[float(p[1]), float(p[0])] for p in raw_coords]

                output.append({
                    "id": u.ward_id or str(u.id),
                    "name": u.ward_name,
                    "area": f"{u.elevation_m}m Avg EL",
                    "crop": "Maize",
                    "geometry": flipped_coords 
                })
        
        return output

    except Exception as e:
        logger.error(f"Failed to fetch regions: {e}")
        return []


@router.post("/query/point", response_model=QueryPointResponse)
def query_point(request: QueryPointRequest, db: Session = Depends(get_db)):
    """
    Queries a specific geographic point, extracts features from a COG stack (from GEE),
    and calls the ML API to predict yield.
    """
    point = request.point
    
    # FIX 1: Convert Pydantic model to dict for SQLAlchemy utilities
    if hasattr(request.date_range, "model_dump"):
        date_range_dict = request.date_range.model_dump()
    else:
        date_range_dict = request.date_range.dict()
    
    # FIX 2: Explicitly type hint the list to avoid Pylance 'Unknown' errors
    assets: List[Any] = get_raster_assets_by_bbox(db, point, date_range_dict)
    
    # FIX 3: Robustly find the PredictorStack asset
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
                aux_data = aux_results[0]
                features_dict.update({
                    'soil_texture': float(getattr(aux_data, 'soil_texture', 0.0)), 
                    'elevation_mean': float(getattr(aux_data, 'elevation_m', 0.0))
                })
        except Exception as e:
            logger.error(f"Error extracting features from stack: {e}")
            raise HTTPException(status_code=500, detail="Spatial feature extraction failed")
    else:
        logger.warning(f"No PredictorStack found for point {point}. Using fallbacks.")
        features_dict = {
            "ndvi_mean": 0.52, "precip_mean": 5.1, "et_mean": 3.8, 
            "elevation_mean": 1850.0, "soil_texture": 2.0, "temp_mean": 21.5
        }

    # Transform dict to Feature list
    features_list = [Feature(name=str(k), value=float(v)) for k, v in features_dict.items()]
    
    # Call ML API for yield prediction
    try:
        predicted_yield = call_ml_api(features_dict)
    except Exception as e:
        logger.error(f"ML API call failed: {e}")
        predicted_yield = 0.0

    # FIX 6: Robust Datetime Handling
    ts_date = datetime(2024, 1, 1) 
    if stack_asset and hasattr(stack_asset, "datetime"):
        raw_dt = stack_asset.datetime
        if isinstance(raw_dt, datetime):
            ts_date = raw_dt
        elif isinstance(raw_dt, str):
            try:
                ts_date = datetime.fromisoformat(raw_dt)
            except ValueError:
                logger.warning(f"Invalid date format: {raw_dt}")

    time_series = [TimeSeriesData(date=ts_date, value=float(features_dict.get("ndvi_mean", 0.0)))]
    
    return QueryPointResponse(
        predicted_yield=float(predicted_yield), 
        features=features_list, 
        time_series=time_series
    )

    logger.debug(f"Type of u.geom: {type(u.geom)}")
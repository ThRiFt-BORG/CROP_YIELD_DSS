from fastapi import APIRouter, Depends, HTTPException, Query
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

@router.get("/counties")
def get_available_counties(db: Session = Depends(get_db)):
    """
    DYNAMIC DISCOVERY: Returns all counties currently in PostGIS 
    and calculates their geographic center for map FlyTo logic.
    """
    try:
        # We use ST_Extent to find the bounding box of the whole county 
        # and ST_Centroid to find the middle point.
        results = db.query(
            models.AuxiliaryData.county_name,
            func.ST_Y(func.ST_Centroid(func.ST_Extent(models.AuxiliaryData.geom))),
            func.ST_X(func.ST_Centroid(func.ST_Extent(models.AuxiliaryData.geom)))
        ).group_by(models.AuxiliaryData.county_name).all()
        
        return [{"name": r[0], "center": [r[1], r[2]]} for r in results if r[0]]
    except Exception as e:
        logger.error(f"County discovery failed: {e}")
        return []

@router.get("/years")
def get_available_years(db: Session = Depends(get_db)):
    """Discovery: Returns all production years available in the database."""
    try:
        years = db.query(models.AuxiliaryData.year).distinct().order_by(models.AuxiliaryData.year.desc()).all()
        return [y[0] for y in years if y[0]]
    except Exception as e:
        logger.error(f"Year discovery failed: {e}")
        return []

@router.get("/regions")
def get_regions(county: Optional[str] = None, year: int = Query(2024), db: Session = Depends(get_db)):
    """
    Pulls boundaries filtered by county AND year.
    Casts geometry to Any to satisfy Pylance type checking.
    """
    try:
        query = db.query(models.AuxiliaryData).filter(models.AuxiliaryData.year == year)
        if county:
            query = query.filter(models.AuxiliaryData.county_name == county)
        
        units = query.all()
        
        if not units:
            logger.warning(f"No regions found for {county} in {year}")
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
                    "county": u.county_name,
                    "year": u.year,
                    "area": f"{getattr(u, 'elevation_m', 'N/A')}m Avg EL",
                    "geometry": flipped_coords 
                })
        
        return output
    except Exception as e:
        logger.error(f"Failed to fetch regions: {e}")
        return []

@router.get("/regions/{ward_id}/stats")
def get_ward_stats(ward_id: str, year: int = Query(2024), db: Session = Depends(get_db)):
    """
    Fetches stats for a specific ward in a specific year.
    Calculates anomaly relative to the county average for that year.
    """
    unit = db.query(models.AuxiliaryData).filter(
        models.AuxiliaryData.ward_id == ward_id,
        models.AuxiliaryData.year == year
    ).first()
    
    if not unit:
        raise HTTPException(status_code=404, detail="County unit data not found for this year")

    # DYNAMIC BASELINE: Average of ALL wards in this County for the selected year
    avg_county_ndvi = db.query(func.avg(models.AuxiliaryData.ndvi_mean)).filter(
        models.AuxiliaryData.county_name == unit.county_name,
        models.AuxiliaryData.year == year
    ).scalar() or 0.48
    
    current_ndvi = float(cast(Any, unit.ndvi_mean) or 0)
    ndvi_anomaly = ((current_ndvi - avg_county_ndvi) / avg_county_ndvi) * 100

    return {
        "name": unit.ward_name,
        "id": unit.ward_id,
        "county": unit.county_name,
        "year": unit.year,
        "status": "Warning" if ndvi_anomaly < -15 else "Stable",
        "biophysical_signature": {
            "NDVI (Biomass)": {
                "val": round(current_ndvi, 3), 
                "dev": f"{round(ndvi_anomaly, 1)}%",
                "desc": "Vegetation vigor vs County mean."
            },
            "Precipitation (mm)": {
                "val": round(float(cast(Any, unit.precip_mean) or 0), 2),
                "dev": None,
                "desc": "Rainfall flux from CHIRPS."
            },
            "Temperature (°C)": {
                "val": round(float(cast(Any, unit.temp_mean) or 0), 1),
                "dev": None,
                "desc": "Surface temperature from ERA5."
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
    time_series = [TimeSeriesData(date=ts_date, value=float(features_dict.get("ndvi_mean", 0.0)))]
    
    return QueryPointResponse(
        predicted_yield=float(predicted_yield), 
        features=features_list, 
        time_series=time_series
    )
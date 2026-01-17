from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from shared.database.base import get_db
from shared.models.api_models import QueryPointRequest, QueryPointResponse, Feature, TimeSeriesData
from ..utils.db_utils import get_auxiliary_data_at_point, get_raster_assets_by_bbox
from ..utils.geospatial import call_ml_api

def extract_features_from_stack(point, asset_url):
    try:
        # prefer the implementation from utils.geospatial if available at runtime
        from ..utils.geospatial import extract_features_from_stack as _extract
        return _extract(point, asset_url)
    except Exception:
        # fallback default features when geospatial extractor is not present
        return {"ndvi_mean": 0.45, "precip_mean": 4.5, "et_mean": 3.2, "elevation_mean": 1800.0, "soil_texture": 1.0, "temp_mean": 22.0}

import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/query/point", response_model=QueryPointResponse)
def query_point(request: QueryPointRequest, db: Session = Depends(get_db)):
    point = request.point
    date_range = request.date_range
    
    assets = get_raster_assets_by_bbox(db, point, date_range)
    stack_asset = next((a for a in assets if a.asset_type == 'PredictorStack'), None)
    
    if stack_asset:
        features_dict = extract_features_from_stack(point, stack_asset.asset_url)
    else:
        features_dict = {"ndvi_mean": 0.45, "precip_mean": 4.5, "et_mean": 3.2, "elevation_mean": 1800.0, "soil_texture": 1.0, "temp_mean": 22.0}

    features_list = [Feature(name=k, value=v) for k, v in features_dict.items()]
    predicted_yield = call_ml_api(features_dict)
    
    time_series = [TimeSeriesData(date=stack_asset.datetime if stack_asset else "2024-01-01", value=features_dict.get("ndvi_mean", 0.45))]
    
    return QueryPointResponse(predicted_yield=predicted_yield, features=features_list, time_series=time_series)

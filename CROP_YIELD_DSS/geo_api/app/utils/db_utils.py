from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from shared.database.models import YieldObservation, AuxiliaryData, RasterAsset
from shared.models.api_models import Point
from datetime import datetime

def get_yield_observations_near_point(db: Session, point: Point, radius_km: float = 1.0) -> List[YieldObservation]:
    """
    Finds historical yield records near a clicked point.
    """
    point_geom = func.ST_SetSRID(func.ST_MakePoint(point.lon, point.lat), 4326)
    # Transform to 3857 (meters) for accurate radius search
    point_geom_3857 = func.ST_Transform(point_geom, 3857)
    
    return db.query(YieldObservation).filter(
        func.ST_DWithin(
            func.ST_Transform(YieldObservation.geom, 3857), 
            point_geom_3857, 
            radius_km * 1000
        )
    ).all()

def get_auxiliary_data_at_point(db: Session, point: Point) -> List[AuxiliaryData]:
    """
    Finds the Ward (AuxiliaryData) that contains the clicked point.
    """
    point_geom = func.ST_SetSRID(func.ST_MakePoint(point.lon, point.lat), 4326)
    
    # ST_Contains is perfect for linking the point to GEE Ward Zonal Stats
    return db.query(AuxiliaryData).filter(
        func.ST_Contains(AuxiliaryData.geom, point_geom)
    ).all()

def get_raster_assets_by_bbox(db: Session, point: Point, date_range: dict) -> List[RasterAsset]:
    """
    Finds the GEE Predictor Stack .tif that covers the clicked point.
    """
    point_geom = func.ST_SetSRID(func.ST_MakePoint(point.lon, point.lat), 4326)
    
    # Handle both ISO strings and datetime objects safely
    start_date = date_range['start']
    if isinstance(start_date, str):
        start_date = datetime.fromisoformat(start_date)
        
    end_date = date_range['end']
    if isinstance(end_date, str):
        end_date = datetime.fromisoformat(end_date)
    
    return db.query(RasterAsset).filter(
        func.ST_Intersects(RasterAsset.bbox, point_geom),
        RasterAsset.datetime >= start_date,
        RasterAsset.datetime <= end_date
    ).order_by(RasterAsset.datetime).all()
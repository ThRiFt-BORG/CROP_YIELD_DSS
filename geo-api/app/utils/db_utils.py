from sqlalchemy.orm import Session
from sqlalchemy import func, text
from shared.database.models import YieldObservation, AuxiliaryData, RasterAsset
from shared.models.api_models import Point
from geoalchemy2.shape import to_shape
from datetime import datetime

# PostGIS spatial functions are used via func.ST_...

def get_yield_observations_near_point(db: Session, point: Point, radius_km: float = 1.0):
    """
    Queries yield observations within a radius of the given point.
    Uses ST_DWithin for PostGIS.
    """
    # Create a PostGIS POINT geometry from the input point
    point_geom = func.ST_SetSRID(func.ST_MakePoint(point.lon, point.lat), 4326)
    
    # Query for points within the radius (in meters) using ST_DWithin
    # ST_DWithin requires the distance to be in the units of the geometry's SRID (degrees for 4326)
    # For accurate distance, we must transform the geometry to a projected system (e.g., 3857) or use ST_DWithin(geom, geom, distance_in_meters, use_spheroid)
    # A simpler, common approach for small distances is to use ST_DWithin with a projected SRID.
    # For this boilerplate, we'll use ST_DWithin with a transformed geometry (to meters)
    
    # Transform point to Web Mercator (SRID 3857) for distance calculation in meters
    point_geom_3857 = func.ST_Transform(point_geom, 3857)
    
    query = db.query(YieldObservation).filter(
        func.ST_DWithin(func.ST_Transform(YieldObservation.geom, 3857), point_geom_3857, radius_km * 1000)
    )
    
    return query.all()

def get_auxiliary_data_at_point(db: Session, point: Point):
    """
    Queries auxiliary data that contains the given point.
    Uses ST_Contains for PostGIS.
    """
    point_geom = func.ST_SetSRID(func.ST_MakePoint(point.lon, point.lat), 4326)
    
    # Query for polygons that contain the point
    query = db.query(AuxiliaryData).filter(
        func.ST_Contains(AuxiliaryData.geom, point_geom)
    )
    
    return query.all()

def get_raster_assets_by_bbox(db: Session, point: Point, date_range: dict):
    """
    Queries raster assets whose bounding box intersects the given point and falls within the date range.
    Uses ST_Intersects for PostGIS.
    """
    point_geom = func.ST_SetSRID(func.ST_MakePoint(point.lon, point.lat), 4326)
    
    start_date = datetime.fromisoformat(date_range['start'])
    end_date = datetime.fromisoformat(date_range['end'])
    
    query = db.query(RasterAsset).filter(
        func.ST_Intersects(RasterAsset.bbox, point_geom),
        RasterAsset.datetime >= start_date,
        RasterAsset.datetime <= end_date
    ).order_by(RasterAsset.datetime)
    
    return query.all()

from sqlalchemy import Column, Integer, String, Float, DateTime, Date, JSON
from shared.database.base import Base
from geoalchemy2 import Geometry

# PostGIS uses SRID 4326 (WGS 84)
SRID = 4326

class Region(Base):
    __tablename__ = "region"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    geom = Column(Geometry(geometry_type='MULTIPOLYGON', srid=SRID), nullable=False)

class YieldObservation(Base):
    """
    Stores ground truth or persisted predictions.
    Naturally supports multi-year via the 'year' column.
    """
    __tablename__ = "yieldobservation"
    id = Column(Integer, primary_key=True, index=True)
    crop_id = Column(String(50), nullable=False, default="Maize")
    year = Column(Integer, nullable=False, index=True) # Indexed for speed
    yield_value = Column(Float, nullable=False)
    
    # Feature columns from GEE ML Samples
    ndvi_mean = Column(Float)
    precip_mean = Column(Float)
    et_mean = Column(Float)
    temp_mean = Column(Float)
    elevation = Column(Float)
    soil_texture = Column(Float)
    
    geom = Column(Geometry(geometry_type='POINT', srid=SRID), nullable=False)

class RasterAsset(Base):
    """
    Tracks GEE Tiff Stacks. 
    Naturally supports multi-year via the 'datetime' column.
    """
    __tablename__ = "rasterasset"
    id = Column(Integer, primary_key=True, index=True)
    asset_url = Column(String(512), nullable=False)
    datetime = Column(DateTime, nullable=False, index=True)
    asset_type = Column(String(50), nullable=False)
    bands = Column(JSON, nullable=True)
    bbox = Column(Geometry(geometry_type='POLYGON', srid=SRID), nullable=False)

class AuxiliaryData(Base):
    """
    Stores GEE Zonal Statistics.
    RECALIBRATED: Now includes 'year' to support multi-temporal analysis.
    """
    __tablename__ = "auxiliarydata"
    id = Column(Integer, primary_key=True, index=True)
    ward_name = Column(String(100), nullable=False)
    ward_id = Column(String(50))
    county_name = Column(String(100), index=True)
    year = Column(Integer, index=True, nullable=False) # NEW: Temporal Dimension
    
    # Biophysical means for that specific year
    ndvi_mean = Column(Float)
    precip_mean = Column(Float)
    et_mean = Column(Float)
    temp_mean = Column(Float)
    elevation_m = Column(Float)
    soil_texture = Column(Float)
    
    geom = Column(Geometry(geometry_type='MULTIPOLYGON', srid=SRID), nullable=False)
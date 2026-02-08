from sqlalchemy import Column, Integer, String, Float, DateTime, Date, JSON
from shared.database.base import Base
from geoalchemy2 import Geometry

# PostGIS uses SRID 4326 (WGS 84)
SRID = 4326

class Region(Base):
    """General administrative reference boundaries."""
    __tablename__ = "region"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    geom = Column(Geometry(geometry_type='MULTIPOLYGON', srid=SRID), nullable=False)

class YieldObservation(Base):
    """
    Stores ML Samples CSV + Ground Truth Yield + System Predictions.
    Includes ensemble breakdowns and biophysical vitals (including ET).
    """
    __tablename__ = "yieldobservation"
    id = Column(Integer, primary_key=True, index=True)
    crop_id = Column(String(50), nullable=False, default="Maize")
    county_name = Column(String(100), index=True)
    year = Column(Integer, nullable=False, index=True)
    yield_value = Column(Float, nullable=False)
    
    # ENSEMBLE BREAKDOWN
    rf_contribution = Column(Float)
    dssat_contribution = Column(Float)
    limiting_factor = Column(String(100))
    
    # BIOPHYSICAL VITALS (Updated to include ET)
    ndvi_mean = Column(Float)
    evi_mean = Column(Float)
    precip_sum = Column(Float)    
    gdd_total = Column(Float)
    et_mean = Column(Float)       # NEW: Evapotranspiration
    temp_mean = Column(Float)
    elevation = Column(Float)
    soil_texture = Column(Float)
    
    geom = Column(Geometry(geometry_type='POINT', srid=SRID), nullable=False)

class RasterAsset(Base):
    """Metadata for GEE Tiff Stacks stored in MinIO."""
    __tablename__ = "rasterasset"
    id = Column(Integer, primary_key=True, index=True)
    asset_url = Column(String(512), nullable=False) 
    datetime = Column(DateTime, nullable=False, index=True)
    asset_type = Column(String(50), nullable=False) 
    bands = Column(JSON, nullable=True) 
    bbox = Column(Geometry(geometry_type='POLYGON', srid=SRID), nullable=False)

class AuxiliaryData(Base):
    """
    Stores GEE Zonal Statistics (Ward/County health).
    Recalibrated for multi-temporal Yield Gap and Water Balance analysis.
    """
    __tablename__ = "auxiliarydata"
    id = Column(Integer, primary_key=True, index=True)
    ward_name = Column(String(100), nullable=False)
    ward_id = Column(String(50)) 
    county_name = Column(String(100), index=True)
    year = Column(Integer, index=True, nullable=False)
    
    # BIOPHYSICAL MEANS
    ndvi_mean = Column(Float)
    precip_sum = Column(Float)
    temp_mean = Column(Float)
    gdd_total = Column(Float)
    et_mean = Column(Float)       # NEW: Evapotranspiration
    elevation_m = Column(Float)
    soil_texture = Column(Float)
    
    # BASELINE DATA
    yield_2020 = Column(Float) 
    
    geom = Column(Geometry(geometry_type='MULTIPOLYGON', srid=SRID), nullable=False)
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
    Stores ML Samples CSV + Ground Truth Yield.
    Updated to store features directly for fast re-training.
    """
    __tablename__ = "yieldobservation"
    id = Column(Integer, primary_key=True, index=True)
    crop_id = Column(String(50), nullable=False, default="Maize")
    year = Column(Integer, nullable=False)
    yield_value = Column(Float, nullable=False)
    
    # Feature columns from GEE ML Samples CSV
    ndvi_mean = Column(Float)
    precip_mean = Column(Float)
    et_mean = Column(Float)
    temp_mean = Column(Float)
    elevation = Column(Float)
    soil_texture = Column(Float)
    
    geom = Column(Geometry(geometry_type='POINT', srid=SRID), nullable=False)

class RasterAsset(Base):
    """
    Tracks the GEE Stacked TIFF in MinIO.
    """
    __tablename__ = "rasterasset"
    id = Column(Integer, primary_key=True, index=True)
    asset_url = Column(String(512), nullable=False) # minio://dss-cogs/stack_2024.tif
    datetime = Column(DateTime, nullable=False)
    asset_type = Column(String(50), nullable=False) # e.g., 'PredictorStack'
    
    # Store band names as JSON for ISO traceability
    bands = Column(JSON, nullable=True) # ['ndvi', 'precip', 'et', 'elevation', 'soil', 'temp']
    
    bbox = Column(Geometry(geometry_type='POLYGON', srid=SRID), nullable=False)

class AuxiliaryData(Base):
    """
    Stores the GEE Zonal Statistics CSV.
    Links Ward Polygons to their mean environmental values.
    """
    __tablename__ = "auxiliarydata"
    id = Column(Integer, primary_key=True, index=True)
    ward_name = Column(String(100), nullable=False)
    ward_id = Column(String(50)) # ADM2_PCODE from GEE
    
    # Mean values calculated via GEE reduceRegions
    ndvi_mean = Column(Float)
    precip_mean = Column(Float)
    et_mean = Column(Float)
    temp_mean = Column(Float)
    elevation_m = Column(Float)
    soil_texture = Column(Float)
    
    geom = Column(Geometry(geometry_type='MULTIPOLYGON', srid=SRID), nullable=False)
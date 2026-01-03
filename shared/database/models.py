from sqlalchemy import Column, Integer, String, Float, DateTime, Date
from shared.database.base import Base
from geoalchemy2 import Geometry

# PostGIS uses SRID 4326
SRID = 4326

class Region(Base):
    __tablename__ = "region"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    # PostGIS MULTIPOLYGON type
    geom = Column(Geometry(geometry_type='MULTIPOLYGON', srid=SRID), nullable=False)

class YieldObservation(Base):
    __tablename__ = "yieldobservation"
    id = Column(Integer, primary_key=True, index=True)
    crop_id = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    yield_value = Column(Float, nullable=False)
    planting_date = Column(Date)
    harvest_date = Column(Date)
    # PostGIS POINT type
    geom = Column(Geometry(geometry_type='POINT', srid=SRID), nullable=False)

class RasterAsset(Base):
    __tablename__ = "rasterasset"
    id = Column(Integer, primary_key=True, index=True)
    asset_url = Column(String(512), nullable=False)
    datetime = Column(DateTime, nullable=False)
    asset_type = Column(String(50), nullable=False)
    # PostGIS POLYGON type for BBOX
    bbox = Column(Geometry(geometry_type='POLYGON', srid=SRID), nullable=False)

class AuxiliaryData(Base):
    __tablename__ = "auxiliarydata"
    id = Column(Integer, primary_key=True, index=True)
    key_name = Column(String(100), nullable=False)
    value_data = Column(Float)
    # PostGIS GEOMETRY type
    geom = Column(Geometry(geometry_type='GEOMETRY', srid=SRID), nullable=False)

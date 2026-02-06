from fastapi import FastAPI, File, UploadFile, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from shared.database.models import RasterAsset 
from sqlalchemy.orm import Session
from typing import List, Dict, Any, cast
import pandas as pd
import io
import json
import logging
import shapely.geometry
from shapely.geometry import shape
from geoalchemy2.shape import to_shape, from_shape

# Shared imports
from shared.models.api_models import IngestMetadata, IngestResponse
from shared.database.base import get_db
from shared.database import models
from shared.database.models import AuxiliaryData, YieldObservation

# App-specific ingestion logic
from app.ingestion.processors import process_and_ingest_raster

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Data Ingestion Service (DIS)",
    description="Multi-temporal Ingestion Pipeline for Kenyan Counties.",
    version="1.3.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/v1/ingest", response_model=IngestResponse)
async def ingest_raster(
    metadata: str = Form(..., description="JSON string containing IngestMetadata"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        metadata_dict = json.loads(metadata)
        ingest_metadata = IngestMetadata(**metadata_dict)
    except Exception as e:
        logger.error(f"Metadata parsing failed: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid metadata JSON format: {e}")

    try:
        asset_url, asset_id = await process_and_ingest_raster(
            file=file,
            metadata=ingest_metadata,
            db=db
        )
        return IngestResponse(
            message="Raster successfully cataloged.",
            asset_url=asset_url,
            asset_id=cast(int, asset_id) 
        )
    except Exception as e:
        logger.error(f"Ingestion process failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/ingest/geojson")
async def ingest_geojson(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    """
    Ingest boundaries. 
    Standardizes ADM columns for the 47 Kenya Counties.
    """
    try:
        content = await file.read()
        data = json.loads(content)
        features = data.get("features", [])
        for f in features:
            props = f.get("properties", {})
            
            # Map standard Kenya GAUL/Shapefile attributes
            ward_id = str(props.get('ADM2_PCODE') or props.get('ward_id') or props.get('id'))
            county_name = props.get('ADM1_EN') or props.get('county_name') or "Unknown"
            ward_name = props.get('ADM2_EN') or props.get('ward_name') or props.get('name')
            year = int(props.get('year', 2024))

            db.add(AuxiliaryData(
                ward_name=ward_name,
                ward_id=ward_id,
                county_name=county_name,
                year=year,
                geom=from_shape(shape(f.get("geometry")), srid=4326),
                ndvi_mean=0.0, 
                precip_mean=0.0,
                temp_mean=0.0,
                et_mean=0.0,
                elevation_m=0.0,
                soil_texture=0.0
            ))
        db.commit()
        return {"status": "success", "message": f"Successfully ingested {len(features)} boundaries."}
    except Exception as e:
        db.rollback()
        logger.error(f"GeoJSON Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/ingest/csv/{table_type}")
async def ingest_csv(
    table_type: str, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    """
    Ingest GEE CSV outputs.
    RECALIBRATED: Performs an UPSERT (Update or Insert) to merge stats with existing GeoJSON shapes.
    """
    content = await file.read()
    df = pd.read_csv(io.BytesIO(content))
    try:
        if table_type == "wards":
            logger.info(f"Merging {len(df)} CSV records with existing spatial units.")
            for _, row in df.iterrows():
                w_id = str(row.get('ward_id') or row.get('ADM2_PCODE'))
                w_year = int(row.get('year', 2024))
                
                existing_unit = db.query(AuxiliaryData).filter(
                    AuxiliaryData.ward_id == w_id,
                    AuxiliaryData.year == w_year
                ).first()

                if existing_unit:
                    # FIX: cast(Any, ...) solves the "float not assignable to Column" Pylance issue
                    u = cast(Any, existing_unit)
                    u.ndvi_mean = float(row.get('ndvi_mean') or row.get('ndvi') or 0.0)
                    u.precip_mean = float(row.get('precip_mean') or row.get('precip') or 0.0)
                    u.temp_mean = float(row.get('temp_mean') or row.get('temp') or 0.0)
                    u.et_mean = float(row.get('et_mean') or row.get('et') or 0.0)
                    u.elevation_m = float(row.get('elevation_mean') or row.get('elevation') or 0.0)
                    u.soil_texture = float(row.get('soil_texture') or 0.0)
                    
                    c_name = row.get('county_name')
                    if c_name:
                        u.county_name = str(c_name)
                else:
                    db.add(AuxiliaryData(
                        ward_name=str(row.get('ward_name') or row.get('ADM2_EN') or "Unknown"),
                        ward_id=w_id,
                        county_name=str(row.get('county_name') or "Unknown"),
                        year=w_year,
                        ndvi_mean=float(row.get('ndvi_mean', 0.0)),
                        precip_mean=float(row.get('precip_mean', 0.0)),
                        temp_mean=float(row.get('temp_mean', 0.0)),
                        et_mean=float(row.get('et_mean', 0.0)),
                        elevation_m=float(row.get('elevation_mean', 0.0)),
                        soil_texture=float(row.get('soil_texture', 0.0)),
                        geom=None 
                    ))
        
        elif table_type == "samples":
            for _, row in df.iterrows():
                lon = float(row.get('longitude') or row.get('lon') or 0.0)
                lat = float(row.get('latitude') or row.get('lat') or 0.0)
                db.add(YieldObservation(
                    crop_id="Maize", 
                    year=int(row.get('year', 2024)),
                    yield_value=float(row.get('yield_value', 0.0)),
                    ndvi_mean=row.get('ndvi'), 
                    precip_mean=row.get('precip'),
                    temp_mean=row.get('temp'), 
                    geom=f"SRID=4326;POINT({lon} {lat})"
                ))
        
        db.commit()
        return {"status": "success", "message": f"Ingested/Merged {len(df)} records into {table_type}"}
    except Exception as e:
        db.rollback()
        logger.error(f"CSV Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/rasters")
def list_rasters(db: Session = Depends(get_db)):
    assets = db.query(RasterAsset).all()
    output = []
    for a in assets:
        dt_val = a.datetime.isoformat() if a.datetime is not None else None
        asset_dict = {
            "id": a.id, 
            "type": a.asset_type, 
            "acquisition_date": dt_val, 
            "format": "COG", 
            "size": "Variable", 
            "region": "Kenya DSS", 
            "status": "Active"
        }
        if a.bbox is not None:
            asset_dict["bbox"] = shapely.geometry.mapping(to_shape(cast(Any, a.bbox)))
        output.append(asset_dict)
    return output

@app.get("/v1/status")
def get_status():
    return {"status": "healthy", "service": "DIS"}
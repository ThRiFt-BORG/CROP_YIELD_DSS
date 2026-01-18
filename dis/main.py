from fastapi import FastAPI, File, UploadFile, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from shared.database.models import RasterAsset # Added this import

from sqlalchemy.orm import Session
from typing import Dict, Any, cast # Added cast
import pandas as pd
import io
import json
import logging

# Shared imports
from shared.models.api_models import IngestMetadata, IngestResponse
from shared.database.base import get_db
from shared.database.models import AuxiliaryData, YieldObservation

# App-specific ingestion logic
from app.ingestion.processors import process_and_ingest_raster

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Data Ingestion Service (DIS)",
    description="ISO-robust pipeline for GEE Raster and Tabular data ingestion.",
    version="1.2.0"
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
    """
    Ingest a GeoTIFF:
    1. Parse JSON metadata.
    2. Convert GeoTIFF to Cloud Optimized GeoTIFF (COG).
    3. Upload to MinIO S3.
    4. Register bbox and band metadata in PostGIS.
    """
    try:
        metadata_dict = json.loads(metadata)
        ingest_metadata = IngestMetadata(**metadata_dict)
    except Exception as e:
        logger.error(f"Metadata parsing failed: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid metadata JSON format: {e}")

    try:
        # process_and_ingest_raster returns (asset_url: str, asset_id: Any)
        asset_url, asset_id = await process_and_ingest_raster(
            file=file,
            metadata=ingest_metadata,
            db=db
        )
        
        # FIX: typing.cast(int, asset_id) tells Pylance to ignore the Column object 
        # and treat the result as a raw integer. This is the cleanest way to fix
        # SQLAlchemy/Pydantic type mismatches.
        return IngestResponse(
            message="Raster successfully processed and cataloged.",
            asset_url=asset_url,
            asset_id=cast(int, asset_id) 
        )
    except Exception as e:
        logger.error(f"Ingestion process failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/ingest/csv/{table_type}")
async def ingest_csv(
    table_type: str, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    """
    Ingest GEE CSV outputs (Wards or Samples).
    """
    content = await file.read()
    df = pd.read_csv(io.BytesIO(content))
    
    try:
        if table_type == "wards":
            logger.info(f"Ingesting {len(df)} ward records.")
            for _, row in df.iterrows():
                db.add(AuxiliaryData(
                    ward_name=row.get('ward_name'),
                    ward_id=str(row.get('ward_id')),
                    ndvi_mean=row.get('ndvi_mean'),
                    precip_mean=row.get('precip_mean'),
                    temp_mean=row.get('temp_mean'),
                    et_mean=row.get('et_mean'),
                    elevation_m=row.get('elevation_mean'),
                    soil_texture=row.get('soil_texture')
                ))
        
        elif table_type == "samples":
            logger.info(f"Ingesting {len(df)} ML pixel samples.")
            for _, row in df.iterrows():
                lon = row.get('longitude') or 0.0
                lat = row.get('latitude') or 0.0
                
                db.add(YieldObservation(
                    crop_id="Maize",
                    year=2024,
                    yield_value=row.get('yield_value', 0.0),
                    ndvi_mean=row.get('ndvi'),
                    precip_mean=row.get('precip'),
                    temp_mean=row.get('temp'),
                    geom=f"SRID=4326;POINT({lon} {lat})"
                ))
        else:
            raise HTTPException(status_code=400, detail="Invalid table_type.")

        db.commit()
        return {"status": "success", "message": f"Ingested {len(df)} rows"}

    except Exception as e:
        db.rollback()
        logger.error(f"CSV Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Database insertion failed: {e}")

@app.get("/v1/rasters")
def list_rasters(db: Session = Depends(get_db)):
    """Used by dashboard to count assets"""
    assets = db.query(RasterAsset).all()
    return assets

@app.get("/v1/status")
def get_status():
    return {"status": "healthy", "service": "DIS"}
from fastapi import FastAPI, File, UploadFile, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Any, cast
import pandas as pd
import io
import json
import logging
import shapely.geometry
from geoalchemy2.shape import to_shape  # FIX: Added missing import

# Shared imports
from shared.models.api_models import IngestMetadata, IngestResponse
from shared.database.base import get_db
from shared.database.models import AuxiliaryData, YieldObservation, RasterAsset

# App-specific ingestion logic
from app.ingestion.processors import process_and_ingest_raster

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="DIS", version="1.2.0")

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
        raise HTTPException(status_code=400, detail=f"Invalid metadata: {e}")

    try:
        asset_url, asset_id = await process_and_ingest_raster(
            file=file,
            metadata=ingest_metadata,
            db=db
        )
        return IngestResponse(
            message="Raster successfully processed.",
            asset_url=asset_url,
            asset_id=cast(int, asset_id) 
        )
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/rasters")
def list_rasters(db: Session = Depends(get_db)):
    """
    FIX: Robust serialization of PostGIS WKBElement.
    This prevents the 'WKBElement is not iterable' crash.
    """
    assets = db.query(RasterAsset).all()
    output = []
    for a in assets:
        # FIX: Access .value or use 'is not None' to avoid SQLAlchemy Column boolean errors
        dt_val = None
        if a.datetime is not None:
            dt_val = a.datetime.isoformat()

        asset_dict = {
            "id": a.id,
            "asset_url": a.asset_url,
            "datetime": dt_val,
            "asset_type": a.asset_type,
            "bands": a.bands,
            "status": "Active"
        }
        
        # FIX: Convert WKBElement to GeoJSON dictionary
        if a.bbox is not None:
            try:
                # to_shape converts binary to a Shapely object
                # mapping converts Shapely object to a JSON-ready dict
                asset_dict["bbox"] = shapely.geometry.mapping(to_shape(cast(Any, a.bbox)))
            except Exception as e:
                logger.error(f"Geometry conversion failed for asset {a.id}: {e}")
                asset_dict["bbox"] = None
        else:
            asset_dict["bbox"] = None
            
        output.append(asset_dict)
    return output

@app.get("/v1/status")
def get_status():
    return {"status": "healthy", "service": "DIS"}

# Add the ingest_csv route here as well if needed...
@app.post("/v1/ingest/csv/{table_type}")
async def ingest_csv(
    table_type: str, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    """
    Ingest GEE CSV outputs:
    1. 'wards' (Zonal Statistics for County Units)
    2. 'samples' (ML Pixel samples with lat/lon)
    """
    logger.info(f"Received request to ingest CSV into table type: {table_type}")
    
    try:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
        
        if df.empty:
            raise HTTPException(status_code=400, detail="The uploaded CSV file is empty.")

        if table_type == "wards":
            logger.info(f"Ingesting {len(df)} administrative records.")
            for _, row in df.iterrows():
                # We use row.get() for robustness in case GEE columns are renamed
                db.add(AuxiliaryData(
                    ward_name=row.get('ward_name') or row.get('county_name'),
                    ward_id=str(row.get('ward_id') or row.get('county_id')),
                    ndvi_mean=float(row.get('ndvi_mean', 0)),
                    precip_mean=float(row.get('precip_mean', 0)),
                    temp_mean=float(row.get('temp_mean', 0)),
                    et_mean=float(row.get('et_mean', 0)),
                    elevation_m=float(row.get('elevation_mean', 0)),
                    soil_texture=float(row.get('soil_texture', 0)),
                    # Note: Geometry ingestion for Wards requires WKT in the CSV
                    # If not present, we create a placeholder based on the GEE ROI
                    geom=row.get('geometry') if 'geometry' in row else None
                ))
        
        elif table_type == "samples":
            logger.info(f"Ingesting {len(df)} ML pixel samples.")
            for _, row in df.iterrows():
                # Correctly handle GEE coordinate names
                lon = float(row.get('longitude') or row.get('lon') or 0.0)
                lat = float(row.get('latitude') or row.get('lat') or 0.0)
                
                db.add(YieldObservation(
                    crop_id="Maize",
                    year=2024,
                    yield_value=float(row.get('yield_value', 0.0)),
                    ndvi_mean=float(row.get('ndvi', 0.0)),
                    precip_mean=float(row.get('precip', 0.0)),
                    temp_mean=float(row.get('temp', 0.0)),
                    # Create PostGIS geometry on the fly
                    geom=f"SRID=4326;POINT({lon} {lat})"
                ))
        else:
            raise HTTPException(status_code=400, detail="Invalid table_type. Use 'wards' or 'samples'.")

        db.commit()
        logger.info(f"Successfully ingested {len(df)} rows into {table_type}.")
        return {"status": "success", "message": f"Successfully ingested {len(df)} records into {table_type}."}

    except Exception as e:
        db.rollback()
        logger.error(f"CSV Ingestion Pipeline failed: {e}")
        raise HTTPException(status_code=500, detail=f"Database ingestion error: {str(e)}")
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
from shapely.geometry import shape  # Added for GeoJSON
from geoalchemy2.shape import to_shape, from_shape  # Added from_shape

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
            message="Raster successfully processed and cataloged.",
            asset_url=asset_url,
            asset_id=cast(int, asset_id) 
        )
    except Exception as e:
        logger.error(f"Ingestion process failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# NEW: GeoJSON Ingestion Endpoint
@app.post("/v1/ingest/geojson")
async def ingest_geojson(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    """Ingest GeoJSON boundaries into AuxiliaryData table."""
    try:
        content = await file.read()
        data = json.loads(content)
        
        if data.get("type") != "FeatureCollection":
            raise HTTPException(status_code=400, detail="Invalid GeoJSON format.")

        features = data.get("features", [])
        for f in features:
            props = f.get("properties", {})
            geom = f.get("geometry")
            
            shapely_geom = shape(geom)
            
            db.add(AuxiliaryData(
                ward_name=props.get('ADM2_EN') or props.get('name') or "Unknown",
                ward_id=str(props.get('ADM2_PCODE') or props.get('id') or "0"),
                ndvi_mean=0.0,
                precip_mean=0.0,
                geom=from_shape(shapely_geom, srid=4326)
            ))

        db.commit()
        return {"status": "success", "message": f"Ingested {len(features)} boundary units."}
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
    content = await file.read()
    df = pd.read_csv(io.BytesIO(content))
    
    try:
        if table_type == "wards":
            for _, row in df.iterrows():
                db.add(AuxiliaryData(
                    ward_name=row.get('ward_name') or row.get('county_name'),
                    ward_id=str(row.get('ward_id') or row.get('county_id')),
                    ndvi_mean=float(row.get('ndvi_mean', 0)),
                    precip_mean=float(row.get('precip_mean', 0)),
                    temp_mean=float(row.get('temp_mean', 0)),
                    et_mean=float(row.get('et_mean', 0)),
                    elevation_m=float(row.get('elevation_mean', 0)),
                    soil_texture=float(row.get('soil_texture', 0)),
                    geom=row.get('geometry') if 'geometry' in row else None
                ))
        elif table_type == "samples":
            for _, row in df.iterrows():
                lon, lat = float(row.get('longitude', 0)), float(row.get('latitude', 0))
                db.add(YieldObservation(
                    crop_id="Maize", year=2024, yield_value=float(row.get('yield_value', 0.0)),
                    ndvi_mean=row.get('ndvi'), precip_mean=row.get('precip'),
                    temp_mean=row.get('temp'), geom=f"SRID=4326;POINT({lon} {lat})"
                ))
        db.commit()
        return {"status": "success", "message": f"Ingested {len(df)} rows"}
    except Exception as e:
        db.rollback()
        logger.error(f"CSV Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/rasters")
def list_rasters(db: Session = Depends(get_db)):
    """
    RECALIBRATED: Matches frontend keys for auto-filling the Raster Assets table.
    """
    assets = db.query(RasterAsset).all()
    output = []
    for a in assets:
        # Format the date nicely for the table
        date_str = a.datetime.strftime("%Y-%m-%d") if a.datetime is not None else "N/A"
        
        asset_dict = {
            "id": a.id,
            "type": a.asset_type,           # Frontend expects 'type'
            "acquisition_date": date_str,   # Frontend expects 'acquisition_date'
            "format": "COG",                # Standard
            "size": "Variable",             
            "region": "Trans Nzoia",        # Local context
            "status": "Active"
        }
        if a.bbox is not None:
            asset_dict["bbox"] = shapely.geometry.mapping(to_shape(cast(Any, a.bbox)))
        output.append(asset_dict)
    return output

@app.get("/v1/status")
def get_status():
    return {"status": "healthy", "service": "DIS"}
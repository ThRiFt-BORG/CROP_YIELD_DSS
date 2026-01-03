from fastapi import FastAPI, File, UploadFile, Form, Depends, HTTPException
from shared.models.api_models import IngestMetadata, IngestResponse
from app.ingestion.processors import process_and_ingest_raster
from shared.database.base import get_db
from sqlalchemy.orm import Session

# Initialize FastAPI app
app = FastAPI(
    title="Data Ingestion Service (DIS)",
    description="Handles raster processing, COG conversion, and metadata ingestion.",
    version="1.0.0"
)

@app.post("/v1/ingest", response_model=IngestResponse)
async def ingest_raster(
    metadata: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Receives a raster file and metadata, converts it to COG, uploads to S3 (Minio),
    and inserts metadata into the MySQL database.
    """
    try:
        # Parse metadata string into Pydantic model
        import json
        metadata_dict = json.loads(metadata)
        ingest_metadata = IngestMetadata(**metadata_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid metadata format: {e}")

    # Process the file
    try:
        asset_url, asset_id = await process_and_ingest_raster(
            file=file,
            metadata=ingest_metadata,
            db=db
        )
        return IngestResponse(
            message="Raster successfully processed, uploaded, and cataloged.",
            asset_url=asset_url,
            asset_id=asset_id if isinstance(asset_id, int) else asset_id.value
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}")

@app.get("/v1/status")
def get_status():
    return {"status": "healthy", "message": "DIS is running"}

import os
import tempfile
import rasterio
from rasterio.enums import Resampling
from fastapi import UploadFile, HTTPException
from shared.models.api_models import IngestMetadata
from shared.database.models import RasterAsset
from sqlalchemy.orm import Session
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
from shapely.geometry import box
from geoalchemy2.shape import from_shape

# Configuration
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minio_user")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minio_password")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "dss-cogs")

s3_client = boto3.client(
    's3',
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
    config=Config(signature_version='s3v4')
)

def convert_to_cog(input_file_path: str, output_file_path: str):
    """Memory-efficient COG conversion writing band-by-band."""
    try:
        with rasterio.open(input_file_path) as src:
            profile = src.profile
            profile.update(
                driver='GTiff',
                tiled=True,
                blockxsize=256,
                blockysize=256,
                compress='LZW',
                interleave='pixel' # Better for COG performance
            )

            with rasterio.open(output_file_path, 'w', **profile) as dst:
                # Loop through bands one by one to save RAM
                for i in range(1, src.count + 1):
                    dst.write(src.read(i), i)
                
                # Build overviews for fast map zooming
                dst.build_overviews([2, 4, 8, 16], Resampling.average)
                dst.update_tags(ns='rio_overview', resampling='average')
        return True
    except Exception as e:
        print(f"ISO-ERROR: COG conversion failed: {e}")
        return False

async def process_and_ingest_raster(file: UploadFile, metadata: IngestMetadata, db: Session):
    # 1. Save temp
    with tempfile.NamedTemporaryFile(delete=False, suffix=".tif") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    cog_path = tmp_path + "_cog.tif"
    
    try:
        # 2. Convert
        if not convert_to_cog(tmp_path, cog_path):
            raise HTTPException(status_code=500, detail="COG conversion failed")

        # 3. Upload to MinIO
        object_name = f"{metadata.asset_type}/{datetime.now().strftime('%Y%m%d')}_{file.filename}"
        s3_client.upload_file(cog_path, S3_BUCKET_NAME, object_name)
        asset_url = f"{MINIO_ENDPOINT}/{S3_BUCKET_NAME}/{object_name}"

        # 4. Extract Spatial Metadata & Band Names
        with rasterio.open(cog_path) as src:
            bounds = src.bounds
            wkt_bbox = box(bounds.left, bounds.bottom, bounds.right, bounds.top)
            # CRITICAL: Capture band names so Geo-API knows where NDVI is
            band_list = list(src.descriptions) if src.descriptions[0] else [f"band_{i+1}" for i in range(src.count)]
            
        asset_datetime = datetime.fromisoformat(metadata.datetime.replace('Z', '+00:00'))

        # 5. Catalog in PostGIS (Matches your updated models.py)
        new_asset = RasterAsset(
            asset_url=asset_url,
            datetime=asset_datetime,
            asset_type=metadata.asset_type,
            bands=band_list, # Saved as JSON
            bbox=from_shape(wkt_bbox, srid=4326)
        )
        
        db.add(new_asset)
        db.commit()
        db.refresh(new_asset)
        return asset_url, new_asset.id

    finally:
        if os.path.exists(tmp_path): os.remove(tmp_path)
        if os.path.exists(cog_path): os.remove(cog_path)
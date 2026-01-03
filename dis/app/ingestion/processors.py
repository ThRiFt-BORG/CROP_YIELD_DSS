import os
import tempfile
import rasterio
from rasterio.io import MemoryFile
from rasterio.enums import Resampling
from fastapi import UploadFile, HTTPException
from shared.models.api_models import IngestMetadata
from shared.database.models import RasterAsset
from sqlalchemy.orm import Session
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from shapely.geometry import box
from geoalchemy2.shape import from_shape

# Configuration
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minio_user")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minio_password")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "dss-cogs")

# Initialize S3 client (Minio compatible)
s3_client = boto3.client(
    's3',
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
    config=boto3.session.Config(signature_version='s3v4')
)

def convert_to_cog(input_file_path: str, output_file_path: str):
    """
    Converts a standard GeoTIFF to a Cloud Optimized GeoTIFF (COG).
    """
    try:
        with rasterio.open(input_file_path) as src:
            profile = src.profile
            
            # Update profile for COG creation
            profile.update(
                driver='GTiff',
                tiled=True,
                blockxsize=256,
                blockysize=256,
                compress='LZW',
                interleave='band'
            )

            # Create overviews (internal pyramids)
            with rasterio.open(output_file_path, 'w', **profile) as dst:
                # Write the data
                dst.write(src.read())
                
                # Build overviews
                factors = [2, 4, 8, 16, 32]
                dst.build_overviews(factors, Resampling.average)
                dst.update_tags(ns='rio_overview', resampling='average')
        
        return True
    except Exception as e:
        print(f"COG conversion failed: {e}")
        return False

async def process_and_ingest_raster(file: UploadFile, metadata: IngestMetadata, db: Session):
    """
    Main ingestion pipeline: save raw, convert to COG, upload to S3, catalog in DB.
    """
    # 1. Save uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    cog_path = tmp_path + "_cog.tif"
    
    try:
        # 2. Convert to COG
        if not convert_to_cog(tmp_path, cog_path):
            raise HTTPException(status_code=500, detail="Failed to convert raster to COG.")

        # 3. Upload COG to S3 (Minio)
        object_name = f"{metadata.asset_type}/{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename.replace(' ', '_')}"
        
        try:
            s3_client.upload_file(cog_path, S3_BUCKET_NAME, object_name)
        except ClientError as e:
            # Attempt to create bucket if it doesn't exist
            if e.response['Error']['Code'] == 'NoSuchBucket':
                s3_client.create_bucket(Bucket=S3_BUCKET_NAME)
                s3_client.upload_file(cog_path, S3_BUCKET_NAME, object_name)
            else:
                raise e

        asset_url = f"{MINIO_ENDPOINT}/{S3_BUCKET_NAME}/{object_name}"

        # 4. Extract metadata for DB cataloging
        with rasterio.open(cog_path) as src:
            bounds = src.bounds
            wkt_bbox = box(bounds.left, bounds.bottom, bounds.right, bounds.top)
            
            # Convert datetime string to Python datetime object
            asset_datetime = datetime.fromisoformat(metadata.datetime.replace('Z', '+00:00'))

            # 5. Insert metadata into MySQL
            new_asset = RasterAsset(
                asset_url=asset_url,
                datetime=asset_datetime,
                asset_type=metadata.asset_type,
                # Use geoalchemy2.shape.from_shape to convert shapely object to WKT for MySQL
                bbox=from_shape(wkt_bbox, srid=4326)
            )
            
            db.add(new_asset)
            db.commit()
            db.refresh(new_asset)
            
            return asset_url, new_asset.id

    finally:
        # 6. Cleanup temporary files
        os.remove(tmp_path)
        if os.path.exists(cog_path):
            os.remove(cog_path)

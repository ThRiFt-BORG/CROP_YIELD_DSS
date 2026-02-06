import requests
import json
import os

BASE_URL = "http://localhost:8002/v1"
# Update these paths to where you saved your GEE downloads
RASTER_PATH = r"D:\WORK\CROP_DSS\CROP_YIELD_DSS\backend\DATA\rasters\trans_nzoia_predictor_stack_2024.tif"
WARD_CSV = r"D:\WORK\CROP_DSS\CROP_YIELD_DSS\backend\DATA\tabular\trans_nzoia_ward_zonal_stats_2024.csv"

def upload_raster():
    if not os.path.exists(RASTER_PATH): return
    metadata = {"asset_type": "PredictorStack", "datetime": "2024-01-01T00:00:00Z"}
    
    with open(RASTER_PATH, 'rb') as f:
        # KEY FIX: Key must be 'file' to match FastAPI
        files = {'file': (os.path.basename(RASTER_PATH), f, 'image/tiff')}
        data = {'metadata': json.dumps(metadata)}
        res = requests.post(f"{BASE_URL}/ingest", files=files, data=data)
        print("Raster Response:", res.json())

def upload_csv():
    if not os.path.exists(WARD_CSV): return
    with open(WARD_CSV, 'rb') as f:
        files = {'file': f}
        res = requests.post(f"{BASE_URL}/ingest/csv/wards", files=files)
        print("CSV Response:", res.json())

if __name__ == "__main__":
    upload_raster()
    upload_csv()
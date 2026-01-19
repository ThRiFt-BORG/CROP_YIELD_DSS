import requests
import json
import os

# Configuration
dis_url = "http://localhost:8002/v1/ingest"
FILE_PATH = r"D:\WORK\CROP_DSS\CROP_YIELD_DSS\ml_api\Data\Trans Nzoia\trans_nzoia_predictor_stack_2024.tif"

if not os.path.exists(FILE_PATH):
    print(f"ERROR: File not found at {FILE_PATH}")
    exit(1)

metadata = {
    "asset_type": "PredictorStack",
    "datetime": "2024-01-01T00:00:00Z",
    "crop_id": "maize"
}

# Prepare the request
with open(FILE_PATH, 'rb') as f:
    # FIX: Key must be 'file' to match FastAPI parameter file: UploadFile
    files = {'file': ('trans_nzoia_stack.tif', f, 'image/tiff')}
    data = {'metadata': json.dumps(metadata)}

    print(f"Uploading {FILE_PATH} to {dis_url}...")
    try:
        response = requests.post(dis_url, files=files, data=data)
        if response.status_code == 200:
            print("SUCCESS!")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"FAILURE: Status {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Network Error: {e}")
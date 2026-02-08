import requests
import json
import os
import sys

# Configuration
DIS_URL = "http://localhost:8002/v1/ingest"

def upload_stack(file_path, county_name, year):
    if not os.path.exists(file_path):
        print(f"ERROR: File not found at {file_path}")
        return

    metadata = {
        "asset_type": "PredictorStack",
        "datetime": f"{year}-01-01T00:00:00Z",
        "crop_id": "Maize",
        "county": county_name
    }

    with open(file_path, 'rb') as f:
        # Key must be 'file' to match DIS main.py
        files = {'file': (os.path.basename(file_path), f, 'image/tiff')}
        data = {'metadata': json.dumps(metadata)}

        print(f"Uploading {county_name} {year} stack...")
        try:
            response = requests.post(DIS_URL, files=files, data=data)
            if response.status_code == 200:
                print(f"SUCCESS: {response.json()['message']}")
            else:
                print(f"FAILURE: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Network Error: {e}")

if __name__ == "__main__":
    # Example usage: python ingest.py "D:\path\to\nakuru_stack.tif" "Nakuru" 2024
    if len(sys.argv) > 3:
        upload_stack(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        # Default fallback to your current file for testing
        DEFAULT_PATH = r"D:\WORK\CROP_DSS\CROP_YIELD_DSS\backend\DATA\rasters\nyandarua_2024_stack_100m.tif"
        upload_stack(DEFAULT_PATH, "Nyandarua", 2024)
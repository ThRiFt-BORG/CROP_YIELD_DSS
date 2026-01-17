import requests
import json
#Configuration
dis_url = "http://localhost:8002/v1/ingest"
FILE_PATH = r"D:\WORK\CROP_DSS\CROP_YIELD_DSS\ml_api\Data\Trans Nzoia\trans_nzoia_predictor_stack_2024.tif"

#Metadata for the sytem
metadata = {
    "asset_type":
    "PredictorStack",
    "datetime":
    "2024-01-01T00:00:00Z",
    "crop_id": "maize"
}

#Prepare the request
with open(FILE_PATH, 'rb') as f:
    files = {'files':f}
    data = {'metadata': json.dumps(metadata)}

    print(f"Uploading {FILE_PATH}...")
    response = requests.post(dis_url, files=files, data=data)
if response.status_code == 200:
    print("SUCCESS!")
    print(response.json())
else:
    print(f"FAILURE:{response.status_code}")
    print(response.text)

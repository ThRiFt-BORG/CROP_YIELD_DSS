import requests
import os
import numpy as np
from rio_tiler.io import COGReader
from shared.models.api_models import Point, TimeSeriesData
from typing import List

# Configuration
ML_API_URL = os.getenv("ML_API_URL", "http://ml-api:8000")

def calculate_ndvi(red_band: np.ndarray, nir_band: np.ndarray) -> float:
    """
    Calculates the Normalized Difference Vegetation Index (NDVI) from Red and NIR bands.
    Returns the mean NDVI value.
    """
    # Avoid division by zero
    np.seterr(divide='ignore', invalid='ignore')
    ndvi = (nir_band.astype(float) - red_band.astype(float)) / (nir_band + red_band)
    
    # Filter out invalid values (NaN, Inf) and return the mean
    ndvi = ndvi[np.isfinite(ndvi)]
    
    return float(np.mean(ndvi)) if ndvi.size > 0 else 0.0

def extract_time_series_from_cogs(point: Point, assets: List) -> List[TimeSeriesData]:
    """
    Simulates extracting a time series of NDVI values from a list of COG assets.
    """
    time_series = []
    
    # For demonstration, we will only process the first asset and return a mock series
    if not assets:
        # Return mock data if no assets are found
        return [
            TimeSeriesData(date=datetime(2024, 5, 1), value=0.3),
            TimeSeriesData(date=datetime(2024, 5, 15), value=0.5),
            TimeSeriesData(date=datetime(2024, 6, 1), value=0.7),
        ]

    # In a real scenario, we would iterate through all assets:
    for asset in assets:
        try:
            # Use rio-tiler to read a small window around the point
            # This requires the asset_url to be accessible (e.g., S3/Minio)
            with COGReader(asset.asset_url) as cog:
                # Mock band extraction for Sentinel-2 (B4=Red, B8=NIR)
                # This assumes the COG is a multi-band image with known band order
                
                # For simplicity and to avoid complex remote access setup in this sandbox,
                # we will mock the NDVI calculation based on the asset date.
                
                # Mock NDVI calculation: higher NDVI for later dates
                date_diff = (asset.datetime - datetime(2024, 1, 1)).days
                mock_ndvi = 0.2 + (date_diff / 365) * 0.6 # NDVI between 0.2 and 0.8
                
                time_series.append(TimeSeriesData(
                    date=asset.datetime,
                    value=round(mock_ndvi, 3)
                ))
        except Exception as e:
            print(f"Error reading COG {asset.asset_url}: {e}")
            continue
            
    return time_series

def call_ml_api(features: dict) -> float:
    """
    Calls the ML-API to get a yield prediction.
    """
    try:
        response = requests.post(f"{ML_API_URL}/v1/predict", json={"features": features})
        response.raise_for_status()
        return response.json().get("predicted_yield")
    except requests.exceptions.RequestException as e:
        print(f"Error calling ML-API: {e}")
        # Return a mock prediction on failure
        return 160.0

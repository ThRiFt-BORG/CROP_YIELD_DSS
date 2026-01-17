import requests
import os
import numpy as np
from rio_tiler.io import COGReader
from shared.models.api_models import Point, TimeSeriesData
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)
ML_API_URL = os.getenv("ML_API_URL", "http://ml-api:8000")

def extract_features_from_stack(point: Point, asset_url: str) -> Dict[str, float]:
    band_names = ['ndvi_mean', 'precip_mean', 'et_mean', 'elevation_mean', 'soil_texture', 'temp_mean']
    try:
        with COGReader(asset_url) as cog:
            point_data = cog.point(point.lon, point.lat)
            values = [float(v) if v is not None else 0.0 for v in point_data]  # Handle None
            return {band_names[i]: values[i] for i in range(min(len(band_names), len(values)))}
    except Exception as e:
        logger.error(f"Error extracting from stack: {e}")
        return {name: 0.0 for name in band_names}

def call_ml_api(features: dict) -> float:
    try:
        response = requests.post(f"{ML_API_URL}/v1/predict", json={"features": features})
        response.raise_for_status()
        return response.json().get("predicted_yield")
    except Exception as e:
        logger.error(f"ML-API Error: {e}")
        return 0.0
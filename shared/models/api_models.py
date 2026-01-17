from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- General Models ---

class Point(BaseModel):
    lon: float = Field(..., description="Longitude of the point.")
    lat: float = Field(..., description="Latitude of the point.")

class DateRange(BaseModel):
    start: str = Field(..., description="Start date (YYYY-MM-DD).")
    end: str = Field(..., description="End date (YYYY-MM-DD).")

# --- geo_api Models ---

class QueryPointRequest(BaseModel):
    point: Point
    date_range: DateRange

class Feature(BaseModel):
    name: str
    value: float

class TimeSeriesData(BaseModel):
    date: datetime
    value: float

class QueryPointResponse(BaseModel):
    predicted_yield: float
    features: List[Feature]
    time_series: List[TimeSeriesData]

# --- ml_api Models ---

class PredictRequest(BaseModel):
    # Updated to use Dict[str, Any] for better Pylance support
    features: Dict[str, Any] = Field(..., description="Dictionary of features for prediction.")

class PredictResponse(BaseModel):
    predicted_yield: float
    # FIX: Added metadata field to support ISO-19157 traceability (RF vs DSSAT stats)
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata about the prediction ensemble.")

# --- DIS Models ---

class IngestMetadata(BaseModel):
    asset_type: str = Field(..., description="Type of asset, e.g., 'Sentinel-2', 'ERA5'.")
    datetime: str = Field(..., description="Acquisition datetime (ISO format).")
    crop_id: Optional[str] = Field(None, description="Optional crop identifier.")

class IngestResponse(BaseModel):
    message: str
    asset_url: str
    asset_id: int
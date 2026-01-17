from fastapi import FastAPI, HTTPException
from shared.models.api_models import PredictRequest, PredictResponse
import joblib
import os
import pandas as pd
import logging
from pydssat import DSSAT  # Updated: Real DSSAT import

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_PATH = "app/models/trained_model.joblib"
app = FastAPI(title="ML-API", version="1.2.0")
MODEL = None

def load_model():
    global MODEL
    if MODEL is None and os.path.exists(MODEL_PATH):
        MODEL = joblib.load(MODEL_PATH)
    return MODEL

@app.on_event("startup")
async def startup_event():
    load_model()

def run_dssat_simulation(features: dict) -> float:
    try:
        dssat = DSSAT(crop='maize')  # Updated: Real simulation
        # Set inputs from GEE features
        dssat.set_weather(features.get('precip_mean', 5.0), features.get('temp_mean', 22.0), features.get('et_mean', 3.0))
        dssat.set_soil(features.get('soil_texture', 2.0), ph=6.5)  # Example pH; fetch from DB
        dssat.set_management(fertilizer=100)  # Default; make dynamic
        result = dssat.run()
        return result.get('yield', 0.0)  # Extract yield
    except Exception as e:
        logger.error(f"DSSAT simulation failed: {e}")
        return 0.0

@app.post("/v1/predict", response_model=PredictResponse)
def predict_yield(request: PredictRequest):
    model = load_model()
    feature_names = ['ndvi_mean', 'precip_mean', 'et_mean', 'elevation_mean', 'soil_texture', 'temp_mean']
    
    try:
        rf_prediction = 0.0
        if model:
            input_df = pd.DataFrame([request.features])
            for col in feature_names:
                if col not in input_df.columns:
                    input_df[col] = 0
            rf_prediction = float(model.predict(input_df[feature_names])[0])
        
        dssat_prediction = run_dssat_simulation(request.features)
        final_prediction = (rf_prediction + dssat_prediction) / 2 if dssat_prediction > 0 else rf_prediction  # Updated: Ensemble logic
        
        return PredictResponse(predicted_yield=final_prediction)
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
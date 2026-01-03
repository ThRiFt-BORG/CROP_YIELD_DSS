from fastapi import FastAPI, Depends, HTTPException
from shared.models.api_models import PredictRequest, PredictResponse
import joblib
import os
import pandas as pd

# Configuration
MODEL_PATH = "app/models/trained_model.joblib"

# Initialize FastAPI app
app = FastAPI(
    title="ML-API",
    description="Machine Learning Inference Service for Crop Yield Prediction.",
    version="1.0.0"
)

# Global variable to hold the loaded model
MODEL = None

def load_model():
    """Loads the trained model from disk."""
    global MODEL
    if MODEL is None:
        try:
            # Note: The train.py script must be run first to create this file
            MODEL = joblib.load(MODEL_PATH)
            print("ML Model loaded successfully.")
        except FileNotFoundError:
            raise RuntimeError(f"Model file not found at {MODEL_PATH}. Run train.py first.")
    return MODEL

@app.on_event("startup")
async def startup_event():
    # Attempt to load the model on startup
    try:
        load_model()
    except RuntimeError as e:
        print(f"Startup Warning: {e}")
        # Allow startup but mark status as unhealthy

@app.get("/v1/status", response_model=dict)
def get_status():
    """Health check endpoint."""
    if MODEL is None:
        return {"status": "unhealthy", "message": "Model not loaded"}
    return {"status": "healthy", "message": "ML-API is running and model is loaded"}

@app.post("/v1/predict", response_model=PredictResponse)
def predict_yield(request: PredictRequest):
    """
    Accepts a dictionary of features and returns a predicted yield value.
    """
    model = load_model()
    if model is None:
        raise HTTPException(status_code=503, detail="ML Model not available.")

    # Convert features dictionary to a DataFrame for the model
    # Ensure feature order matches the training data (train.py)
    feature_names = ['ndvi_mean', 'elevation', 'soil_type', 'temp_avg']
    
    try:
        # Create a DataFrame from the single request
        features_df = pd.DataFrame([request.features])
        
        # Reindex to ensure correct feature order
        features_df = features_df.reindex(columns=feature_names, fill_value=0)
        
        # Predict
        prediction = model.predict(features_df)[0]
        
        return PredictResponse(predicted_yield=float(prediction))
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction failed: {e}")

# Note: The Procfile will use gunicorn to run this app
# web: gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT

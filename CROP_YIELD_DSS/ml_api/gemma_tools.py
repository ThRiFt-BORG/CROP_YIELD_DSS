import pandas as pd
import os
import joblib

# Load RF model
MODEL_PATH = "ml_api/models/trained_model.joblib"
RF_MODEL = None

def get_rf_model():
    global RF_MODEL
    if RF_MODEL is None and os.path.exists(MODEL_PATH):
        RF_MODEL = joblib.load(MODEL_PATH)
    return RF_MODEL


def run_dssat_sim(features: dict):
    base_potential = 4.2
    precip = float(features.get('precip_total', 600.0))
    temp = float(features.get('temp_mean', 22.0))
    fert = float(features.get('fertilizer', 120.0))

    water_stress = min(1.0, precip / 800.0)
    heat_stress = 1.0 - max(0, (temp - 28) * 0.1)
    n_factor = 0.5 + (0.5 * (fert / 180.0)) if fert < 180 else 1.15

    sim_yield = base_potential * water_stress * heat_stress * n_factor

    return float(sim_yield)


def predict_yield_simple(features: dict):
    rf_model = get_rf_model()

    rf_input = pd.DataFrame([{
        'year': float(features.get('year', 2024)),
        'latitude': float(features.get('lat', 1.0)),
        'longitude': float(features.get('lon', 36.0)),
        'ndvi_mean': float(features.get('ndvi_mean', 0.55)),
        'precip_total': float(features.get('precip_total', 600.0)),
        'gdd_total': float(features.get('gdd_total', 1400.0)),
        'elevation_mean': float(features.get('elevation', 1800.0)),
        'soil_texture': float(features.get('soil_texture', 2)),
        'fertilizer': float(features.get('fertilizer', 120.0)),
        'temp_mean': float(features.get('temp_mean', 22.0))
    }]).astype('float64')

    rf_pred = float(rf_model.predict(rf_input)[0]) if rf_model else 0.0
    dssat_pred = run_dssat_sim(features)

    final = (rf_pred + dssat_pred) / 2 if dssat_pred > 0 else rf_pred

    return {
        "predicted_yield": round(final, 3),
        "rf": round(rf_pred, 3),
        "dssat": round(dssat_pred, 3)
    }
from pydssat import DSSAT  # Import wrapper
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .crud import get_db  # From your CRUD

router = APIRouter()

@router.post("/simulate")
def run_dssat_simulation(crop_id: int, features: dict, db: Session = Depends(get_db)):
    # Fetch additional data from PostGIS (e.g., soil from AuxiliaryData)
    soil_data = db.query(models.AuxiliaryData).filter(models.AuxiliaryData.region_id == features['region_id']).first()

    # Prepare DSSAT inputs (example for maize)
    dssat = DSSAT(crop='maize')  # Initialize for maize
    dssat.set_weather(features['date'], features['precip'], features['temp_c'], features['solar_rad'])  # From GEE
    dssat.set_soil(soil_data.soil_type, soil_data.ph)  # From DB
    dssat.set_management(fertilizer_rate=features.get('fertilizer', 100))  # User input

    # Run simulation
    result = dssat.run()
    yield_sim = result['yield']  # Extract simulated yield (t/ha)

    # Ensemble with existing RF (hybrid)
    rf_pred = your_rf_model.predict(features)  # From existing code
    final_yield = (yield_sim + rf_pred) / 2  # Simple average; tune as needed

    # Store in YieldObservation (PDF Page 6)
    new_obs = models.YieldObservation(yield_value=final_yield, year=2024, region_id=features['region_id'])
    db.add(new_obs)
    db.commit()

    return {"predicted_yield": final_yield, "unit": "t/ha", "model_version": "dssat-hybrid-1.0"}
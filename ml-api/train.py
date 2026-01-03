import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import joblib
from sqlalchemy import create_engine, text
import os

# Configuration
DATABASE_URL = os.getenv("", "mysql+pymysql://user:password@mysql/dss_db")
MODEL_PATH = "ml-api/app/models/trained_model.joblib"

def generate_dummy_features(n_samples=100):
    """Generates synthetic features based on expected DB schema."""
    np.random.seed(42)
    data = {
        'ndvi_mean': np.random.uniform(0.2, 0.8, n_samples),
        'elevation': np.random.uniform(50, 500, n_samples),
        'soil_type': np.random.randint(1, 5, n_samples),
        'temp_avg': np.random.uniform(15, 30, n_samples),
        'yield_value': (np.random.normal(150, 20, n_samples) + 
                        (np.random.uniform(0.2, 0.8, n_samples) * 50) + 
                        (np.random.uniform(50, 500, n_samples) * 0.05))
    }
    df = pd.DataFrame(data)
    return df

def train_and_save_model():
    """
    Trains a RandomForestRegressor model using data from the yieldobservation table
    (or synthetic data if DB connection fails) and saves it.
    """
    print("Attempting to connect to database and fetch training data...")
    try:
        engine = create_engine(DATABASE_URL)
        # In a real scenario, we would join yieldobservation with rasterasset and auxiliarydata
        # For this dummy script, we will just fetch yield_value and generate synthetic features
        with engine.connect() as connection:
            # Simple query to check connection and fetch yield values
            result = connection.execute(text("SELECT yield_value FROM yieldobservation"))
            yield_values = [row[0] for row in result]
        
        n_samples = len(yield_values)
        if n_samples < 10:
            print("Not enough real data found. Generating synthetic data.")
            df = generate_dummy_features(100)
        else:
            print(f"Found {n_samples} yield observations. Generating synthetic features.")
            df = generate_dummy_features(n_samples)
            df['yield_value'] = yield_values # Overwrite synthetic yields with real ones

    except Exception as e:
        print(f"Database connection failed or data fetch error: {e}. Generating fully synthetic data.")
        df = generate_dummy_features(100)

    X = df.drop('yield_value', axis=1)
    y = df['yield_value']

    # Train the model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

    # Save the model
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"Model trained and saved successfully to {MODEL_PATH}")

if __name__ == "__main__":
    train_and_save_model()

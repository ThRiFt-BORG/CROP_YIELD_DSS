import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, r2_score
import joblib
from sqlalchemy import create_engine, text
import os
import logging
import argparse
import random

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
DEFAULT_DB_URL = "postgresql+psycopg2://user:password@postgres/dss_db"  # Placeholder; set via env or arg
MODEL_VERSION_TABLE = "ModelVersion"  # From PDF schema

def parse_args():
    parser = argparse.ArgumentParser(description="Train crop yield model for DSS ML-API.")
    parser.add_argument('--db-url', type=str, default=os.getenv("DATABASE_URL", DEFAULT_DB_URL), help="Database connection URL.")
    parser.add_argument('--model-path', type=str, default="ml-api/app/models/trained_model.joblib", help="Path to save trained model.")
    parser.add_argument('--min-samples', type=int, default=50, help="Minimum real samples before using synthetics.")
    return parser.parse_args()

def generate_synthetic_data(n_samples=1000):
    """Enhanced synthetic data with realistic ranges/correlations for maize (Nakuru context)."""
    logger.info(f"Generating {n_samples} synthetic samples.")
    np.random.seed(42)
    ndvi_mean = np.random.uniform(0.4, 0.7, n_samples)  # From your sample: ~0.43-0.49
    elevation = np.random.uniform(1500, 2500, n_samples)  # Typical for Nakuru
    soil_type = np.random.choice([1, 2, 3, 4], n_samples)  # 1=Clay, 2=Loam, etc.
    temp_avg = np.random.uniform(15, 25, n_samples)  # Mild climate

    # Correlated yield: Base 2000 + NDVI boost + elevation/temp effects + noise
    yields = (
        2000 +
        (ndvi_mean * 4000) +  # Strong NDVI correlation
        (elevation * 0.5) +   # Slight elevation boost
        (temp_avg * 50) +     # Temp boost
        np.random.normal(0, 300, n_samples)  # Noise
    )
    yields = np.clip(yields, 500, 5000)  # Realistic maize range

    df = pd.DataFrame({
        'ndvi_mean': ndvi_mean,
        'elevation': elevation,
        'soil_type': soil_type,
        'temp_avg': temp_avg,
        'yield_value': yields
    })
    return df

def fetch_real_data(engine, min_samples):
    """Fetch joined data from DB (YieldObservation + RasterAsset + AuxiliaryData)."""
    query = text("""
        SELECT 
            yo.yield_value,
            ra.variable AS ndvi_mean,  -- Assuming 'ndvi_mean' stored here; adjust if needed
            ad.elevation_m AS elevation,
            ad.soil_type,
            ad.temp_avg
        FROM yieldobservation yo
        JOIN rasterasset ra ON yo.obs_id = ra.asset_id  -- Adjust JOIN condition based on your schema
        JOIN auxiliarydata ad ON yo.obs_id = ad.aux_id  -- Adjust as needed
        WHERE yo.yield_value IS NOT NULL
    """)
    try:
        df = pd.read_sql(query, engine)
        if len(df) < min_samples:
            logger.warning(f"Only {len(df)} real samples found; supplementing with synthetics.")
            synth_df = generate_synthetic_data(min_samples - len(df))
            df = pd.concat([df, synth_df], ignore_index=True)
        logger.info(f"Fetched/processed {len(df)} samples.")
        return df
    except Exception as e:
        logger.error(f"DB query failed: {e}. Falling back to fully synthetic data.")
        return generate_synthetic_data(1000)

def preprocess_data(df):
    """Clean and preprocess: Handle nulls, encode categoricals, scale numerics."""
    df = df.dropna(subset=['yield_value'])  # Drop if target missing
    df = df.fillna(df.median(numeric_only=True))  # Impute numerics

    numeric_features = ['ndvi_mean', 'elevation', 'temp_avg']
    categorical_features = ['soil_type']

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_features),
            ('cat', OneHotEncoder(sparse_output=False, handle_unknown='ignore'), categorical_features)
        ]
    )
    return preprocessor, df

def train_model(X, y):
    """Train with split, tuning, evaluation."""
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    param_grid = {
        'n_estimators': [50, 100, 200],
        'max_depth': [None, 10, 20]
    }
    model = RandomForestRegressor(random_state=42)
    grid_search = GridSearchCV(model, param_grid, cv=5, scoring='neg_mean_squared_error')
    grid_search.fit(X_train, y_train)
    
    best_model = grid_search.best_estimator_
    y_pred = best_model.predict(X_test)
    
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    logger.info(f"Model metrics: MSE={mse:.2f}, R²={r2:.2f}, Best params={grid_search.best_params_}")
    
    return best_model, r2  # Return accuracy for DB

def save_model_and_metadata(model, model_path, engine, accuracy):
    """Save model artifact and update ModelVersion table."""
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(model, model_path)
    logger.info(f"Model saved to {model_path}")
    
    # Simulate semantic versioning; increment based on existing
    insert_query = text(f"""
        INSERT INTO {MODEL_VERSION_TABLE} (version, accuracy, created_at)
        VALUES ('1.0.1', :accuracy, CURRENT_TIMESTAMP)  -- Adjust version logic
    """)
    with engine.connect() as conn:
        conn.execute(insert_query, {'accuracy': accuracy})
        conn.commit()
    logger.info("Model metadata inserted into DB.")

def main():
    args = parse_args()
    engine = create_engine(args.db_url)
    
    df = fetch_real_data(engine, args.min_samples)
    preprocessor, df = preprocess_data(df)
    
    X = df.drop('yield_value', axis=1)
    y = df['yield_value']
    
    # Apply preprocessing in pipeline
    pipeline = Pipeline(steps=[('preprocessor', preprocessor)])
    X_processed = pipeline.fit_transform(X)
    
    model, accuracy = train_model(X_processed, y)
    save_model_and_metadata(model, args.model_path, engine, accuracy)

if __name__ == "__main__":
    main()
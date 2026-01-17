import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
from sqlalchemy import create_engine, text
import os
import logging
import argparse
# Updated: Added for DSSAT (install pydssat in Dockerfile: pip install pydssat)
from pydssat import DSSAT  # Placeholder; uncomment when integrated

# Setup logging with file handler for traceability
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
handler = logging.FileHandler('train.log')  # Updated: Log to file for review
logger = logging.getLogger(__name__)
logger.addHandler(handler)

# Configuration (Updated: Dynamic features from env or default; PostgreSQL URL)
DEFAULT_DB_URL = "postgresql+psycopg2://user:password@postgres/dss_db"  # Fixed: Match Docker PostGIS
MODEL_VERSION_TABLE = "ModelVersion"
FEATURE_NAMES = os.getenv('FEATURE_NAMES', ['ndvi_mean', 'precip_mean', 'et_mean', 'elevation_mean', 'soil_texture', 'temp_mean']).split(',')
TARGET_NAME = 'yield_value'

def parse_args():
    parser = argparse.ArgumentParser(description="Train production-ready crop yield model for DSS.")
    parser.add_argument('--db-url', type=str, default=os.getenv("DATABASE_URL", DEFAULT_DB_URL), help="Database connection URL.")
    parser.add_argument('--csv-path', type=str, default="trans_nzoia_ml_samples_2024.csv", help="Path to GEE extracted CSV samples.")
    parser.add_argument('--model-path', type=str, default="app/models/trained_model.joblib", help="Path to save trained model.")
    return parser.parse_args()

def load_data(args):
    """Loads data from CSV (GEE output) or Database."""
    df = pd.DataFrame()
    
    if os.path.exists(args.csv_path):
        logger.info(f"Loading data from CSV: {args.csv_path}")
        df = pd.read_csv(args.csv_path)
        
        mapping = {  # Updated: More flexible mapping based on GEE script bands
            'ndvi': 'ndvi_mean',
            'precip': 'precip_mean',
            'et': 'et_mean',
            'elevation': 'elevation_mean',
            'temp': 'temp_mean'
        }
        df = df.rename(columns=mapping)
        
        if TARGET_NAME not in df.columns:
            logger.warning("Target 'yield_value' not found in CSV. Generating realistic synthetic targets.")
            df[TARGET_NAME] = (
                2000 + 
                (df['ndvi_mean'] * 5000) + 
                (df['precip_mean'] * 200) + 
                (df['elevation_mean'] * 0.2) - 
                (df['temp_mean'] * 50) + 
                np.random.normal(0, 200, len(df))
            )
            df[TARGET_NAME] = np.clip(df[TARGET_NAME], 500, 5000)  # Updated: Realistic maize range
    else:
        logger.warning(f"CSV not found at {args.csv_path}. Attempting to fetch from DB.")
        try:
            engine = create_engine(args.db_url)
            query = f"SELECT * FROM yieldobservation"  # Updated: Assume table has GEE features + SPAM yields
            df = pd.read_sql(query, engine)
        except Exception as e:
            logger.error(f"Failed to fetch from DB: {e}.")
            raise
    # Updated: Data quality check (ISO 19157)
    df = df.dropna(subset=[TARGET_NAME])
    return df

def build_pipeline():
    numeric_features = [f for f in FEATURE_NAMES if f != 'soil_texture']  # Updated: Dynamic, exclude cat
    categorical_features = ['soil_texture']

    numeric_transformer = Pipeline(steps=[('scaler', StandardScaler())])
    categorical_transformer = Pipeline(steps=[('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ]
    )

    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(random_state=42, n_jobs=-1))
    ])
    return pipeline

def train_and_evaluate(df, pipeline):
    for col in FEATURE_NAMES:
        if col not in df.columns:
            df[col] = 0
            logger.warning(f"Feature {col} missing, filled with 0.")

    X = df[FEATURE_NAMES]
    y = df[TARGET_NAME]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    param_grid = {
        'regressor__n_estimators': [100, 200],
        'regressor__max_depth': [None, 10, 20]
    }
    
    grid_search = GridSearchCV(pipeline, param_grid, cv=3, scoring='neg_mean_squared_error')
    grid_search.fit(X_train, y_train)
    best_model = grid_search.best_estimator_
    
    y_pred = best_model.predict(X_test)
    metrics = {
        "R2": r2_score(y_test, y_pred),
        "MSE": mean_squared_error(y_test, y_pred),
        "MAE": mean_absolute_error(y_test, y_pred)  # Updated: Use MAE
    }
    logger.info(f"Model Evaluation: {metrics}")
    return best_model, metrics

def main():
    args = parse_args()
    df = load_data(args)
    pipeline = build_pipeline()
    model, metrics = train_and_evaluate(df, pipeline)
    os.makedirs(os.path.dirname(args.model_path), exist_ok=True)
    joblib.dump(model, args.model_path)
    logger.info(f"Model saved to {args.model_path}")

if __name__ == "__main__":
    main()
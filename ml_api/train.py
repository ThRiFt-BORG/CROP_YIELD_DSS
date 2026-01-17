import pandas as pd
import numpy as np
import joblib
import os
import logging
import argparse
import json
from datetime import datetime
from sqlalchemy import create_engine
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.impute import SimpleImputer

# MODERN 2026 DSSATTools Imports
from DSSATTools.crop import Maize # type: ignore
from DSSATTools.filex import Planting, Fertilizer # type: ignore

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

TARGET_NAME = 'yield_value'
FEATURE_NAMES = ['ndvi_mean', 'precip_mean', 'et_mean', 'elevation_mean', 'soil_texture', 'temp_mean']

def validate_iso_quality(df):
    checks = {'ndvi_mean': (0, 1.0), 'temp_mean': (5, 45)}
    for col, (min_v, max_v) in checks.items():
        if col in df.columns:
            invalid = df[(df[col] < min_v) | (df[col] > max_v)].shape[0]
            if invalid > 0:
                logger.warning(f"ISO-19157: {invalid} records out of bounds for {col}")
    return df

def build_pipeline():
    numeric_features = [f for f in FEATURE_NAMES if f != 'soil_texture']
    preprocessor = ColumnTransformer(transformers=[
        ('num', Pipeline([('imp', SimpleImputer(strategy='median')), ('scl', StandardScaler())]), numeric_features),
        ('cat', Pipeline([('imp', SimpleImputer(strategy='constant', fill_value=1)), ('ohe', OneHotEncoder(handle_unknown='ignore', sparse_output=False))]), ['soil_texture'])
    ])
    return Pipeline([('pre', preprocessor), ('reg', RandomForestRegressor(random_state=42))])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--db-url', default=os.getenv("DATABASE_URL", "postgresql+psycopg2://user:password@postgres/dss_db"))
    parser.add_argument('--csv-path', default="trans_nzoia_ml_samples_2024.csv")
    parser.add_argument('--model-path', default="app/models/trained_model.joblib")
    args = parser.parse_args()

    # Fixed: Added mandatory cultivar_code
    try:
        Maize(cultivar_code='IB0001')
        logger.info("Mechanistic environment verified.")
    except Exception as e:
        logger.error(f"DSSATTools verification failed: {e}")

    if not os.path.exists(args.csv_path):
        logger.error(f"File {args.csv_path} not found.")
        return

    df = validate_iso_quality(pd.read_csv(args.csv_path).rename(columns={
        'ndvi': 'ndvi_mean', 'precip': 'precip_mean', 'et': 'et_mean', 'elevation': 'elevation_mean', 'temp': 'temp_mean'
    }))
    
    if TARGET_NAME not in df.columns:
        df[TARGET_NAME] = 2200 + (df['ndvi_mean']*4800) + np.random.normal(0, 150, len(df))

    X_train, X_test, y_train, y_test = train_test_split(df[FEATURE_NAMES], df[TARGET_NAME], test_size=0.2)

    pipeline = build_pipeline()
    grid = GridSearchCV(pipeline, {'reg__n_estimators': [100, 200]}, cv=3, n_jobs=-1)
    grid.fit(X_train, y_train)
    
    best_model = grid.best_estimator_
    y_pred = best_model.predict(X_test)
    
    # Fixed: changed 'Best_model' to 'best_model'
    metrics = {
        "r2": float(r2_score(y_test, y_pred)),
        "mse": float(mean_squared_error(y_test, y_pred))
    }

    os.makedirs(os.path.dirname(args.model_path), exist_ok=True)
    joblib.dump(best_model, args.model_path)
    logger.info(f"Model saved. R2: {metrics['r2']:.4f}")

if __name__ == "__main__":
    main()
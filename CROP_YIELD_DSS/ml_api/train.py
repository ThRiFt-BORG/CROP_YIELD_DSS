import pandas as pd
import numpy as np
import joblib
import os
import logging
import argparse
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, GridSearchCV, GroupKFold
from sklearn.preprocessing import StandardScaler, OneHotEncoder, PolynomialFeatures
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.impute import SimpleImputer

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

TARGET_NAME = 'yield_value'
# Recalibrated Features
FEATURE_NAMES = [
    'year', 'latitude', 'longitude', 
    'ndvi_mean', 'precip_total', 'gdd_total', 
    'elevation_mean', 'soil_texture', 'fertilizer'
]

def validate_iso_quality(df):
    """ISO-19157: Removes biophysical noise (e.g. high NDVI in non-crop areas)."""
    initial_count = len(df)
    # Filter out forest/wetland noise where high NDVI exists but SPAM yield is zero
    df = df[~((df['ndvi_mean'] > 0.6) & (df['yield_value'] < 0.5))]
    logger.info(f"Data Cleaning: Removed {initial_count - len(df)} inconsistent samples.")
    return df

def build_pipeline():
    """
    RECALIBRATED: Implements Non-Linear Interaction Modeling.
    Uses PolynomialFeatures to capture Elevation x Temperature interactions.
    """
    numeric_features = ['year', 'latitude', 'longitude', 'ndvi_mean', 
                        'precip_total', 'gdd_total', 'elevation_mean', 'fertilizer']
    categorical_features = ['soil_texture']

    # Numeric Pipeline with Interaction Terms
    numeric_transformer = Pipeline(steps=[
        ('imp', SimpleImputer(strategy='median')),
        # interaction_only=True prevents squaring variables (e.g. lat^2) 
        # and focuses on combinations (e.g. Elevation x GDD)
        ('poly', PolynomialFeatures(degree=2, interaction_only=True)), 
        ('scl', StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ('imp', SimpleImputer(strategy='constant', fill_value=1)),
        ('ohe', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ]
    )

    return Pipeline([
        ('pre', preprocessor), 
        ('reg', RandomForestRegressor(random_state=42, n_jobs=-1))
    ])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv-path', default="ml_api/Data/master_kenya_ml_2024.csv")
    parser.add_argument('--model-path', default="ml_api/models/trained_model.joblib")
    args = parser.parse_args()

    if not os.path.exists(args.csv_path):
        logger.error(f"File {args.csv_path} not found.")
        return

    # 1. LOAD AND HARMONIZE
    raw_df = pd.read_csv(args.csv_path)
    mapping = {
        'ndvi': 'ndvi_mean', 'precip_sum': 'precip_total', 
        'gdd_total': 'gdd_total', 'elevation': 'elevation_mean', 
        'soil': 'soil_texture', 'lon': 'longitude', 'lat': 'latitude', 
        'yield_value': 'yield_value', 'county': 'county_group'
    }
    df = raw_df.rename(columns=mapping)

    # 2. DATA AUGMENTATION (Fertilizer Sensitivity)
    logger.info("Augmenting data for Nitrogen Response modeling...")
    augmented_data = []
    for _, row in df.iterrows():
        for n_level in [0, 50, 100, 150, 250]:
            new_row = row.copy()
            new_row['fertilizer'] = n_level
            # Linear-Plateau Response Logic
            n_factor = 0.5 + (0.5 * (n_level / 180)) if n_level < 180 else 1.15
            new_row['yield_value'] *= n_factor
            augmented_data.append(new_row)
    
    df = pd.DataFrame(augmented_data)
    df = validate_iso_quality(df)

    # 3. GROUPED K-FOLD VALIDATION
    # We group by 'county_group' so the model is tested on its ability 
    # to generalize to DIFFERENT geographical regions.
    groups = df['county_group']
    X = df[FEATURE_NAMES]
    y = df[TARGET_NAME]
    
    # Define Grouped Cross-Validation
    gkf = GroupKFold(n_splits=3) 

    logger.info(f"Starting Grouped K-Fold training across {len(groups.unique())} counties...")
    
    pipeline = build_pipeline()
    
    # Grid search specifically using the groups to prevent spatial leakage
    grid = GridSearchCV(
        pipeline, 
        param_grid={'reg__n_estimators': [100, 200]}, 
        cv=gkf, 
        n_jobs=-1
    )
    
    grid.fit(X, y, groups=groups)
    
    best_model = grid.best_estimator_
    
    # 4. PERSIST
    os.makedirs(os.path.dirname(args.model_path), exist_ok=True)
    joblib.dump(best_model, args.model_path)
    
    logger.info(f"National Model Saved. Best CV Score: {grid.best_score_:.4f}")

if __name__ == "__main__":
    main()
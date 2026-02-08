import pandas as pd
import glob
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def combine_gee_samples(input_folder, output_file):
    """
    Finds all GEE sample CSVs, maps GEE band names to Model feature names, 
    adds county labels, and merges them.
    """
    # 1. Find all relevant CSV files in the folder
    search_pattern = os.path.join(input_folder, "*_ml_samples_100m.csv")
    file_list = glob.glob(search_pattern)
    
    if not file_list:
        logger.error(f"No files found in {input_folder} matching pattern *_ml_samples_100m.csv")
        return

    all_dataframes = []

    # These are the columns EXACTLY as they appear in your GEE Export CSV
    # Note: 'precip_total' matches your GEE rename('precip_total')
    # Note: 'yield_value' matches your GEE .set('yield_value', ...)
    gee_column_names = [
        'ndvi', 'precip_total', 'gdd_total', 'elevation', 
        'soil', 'yield_value', 'longitude', 'latitude', 'year'
    ]

    for file_path in file_list:
        filename = os.path.basename(file_path)
        logger.info(f"Processing: {filename}")
        
        # 2. Extract County name from the filename
        # Example: nakuru_2024_ml_samples_100m.csv -> Nakuru
        county_name = filename.split('_')[0].title() 
        
        # 3. Read the CSV
        df = pd.read_csv(file_path)
        
        # 4. Validation Check
        missing = [col for col in gee_column_names if col not in df.columns]
        if missing:
            logger.warning(f"File {filename} is missing columns: {missing}. Skipping.")
            continue
            
        # 5. Add the 'county' group for Grouped K-Fold
        df['county'] = county_name
        
        # 6. Standardization Mapping
        # We rename the raw GEE bands to the names our train.py expects
        mapping = {
            'ndvi': 'ndvi_mean',
            'precip_total': 'precip_total',
            'et': 'et_mean',
            'gdd_total': 'gdd_total',
            'elevation': 'elevation_mean',
            'soil': 'soil_texture',
            'longitude': 'longitude',
            'latitude': 'latitude',
            'year': 'year',
            'yield_value': 'yield_value'
        }
        df = df.rename(columns=mapping)
        
        all_dataframes.append(df)

    if all_dataframes:
        # 7. Concatenate all counties into one master dataframe
        master_df = pd.concat(all_dataframes, ignore_index=True)
        
        # 8. Data Cleaning: Remove rows where yield is 0 or NaN 
        # (Usually means pixel was outside the SPAM baseline)
        initial_len = len(master_df)
        master_df = master_df[master_df['yield_value'] > 0].dropna(subset=['yield_value'])
        
        # 9. Save the Master Training Set
        master_df.to_csv(output_file, index=False)
        
        logger.info("--- Combination Complete ---")
        logger.info(f"Total Counties merged: {len(all_dataframes)}")
        logger.info(f"Cleaned samples (Yield > 0): {len(master_df)} (Removed {initial_len - len(master_df)})")
        logger.info(f"Master file saved to: {output_file}")
    else:
        logger.error("No valid data was found to combine. Check if GEE column names match.")

if __name__ == "__main__":
    # Path relative to the project root
    DATA_DIR = "ml_api/Data"
    OUTPUT_PATH = os.path.join(DATA_DIR, "master_kenya_ml_2024.csv")
    
    combine_gee_samples(DATA_DIR, OUTPUT_PATH)
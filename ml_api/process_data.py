import pandas as pd
import numpy as np
import random
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend to avoid Tkinter/Tcl issues
import matplotlib.pyplot as plt
import argparse
import os

# ==========================================
# CONFIGURATION
# ==========================================
def parse_args():
    parser = argparse.ArgumentParser(description="Process GEE NDVI data into synthetic ML training data.")
    parser.add_argument('--input', type=str, default=r'D:\WORK\CROP_DSS\CROP_YIELD_DSS\ml_api\Data\ee-chart.csv', 
                        help="Path to input NDVI CSV (relative or absolute).")
    parser.add_argument('--output', type=str, default=r'D:\WORK\CROP_DSS\CROP_YIELD_DSS\ml_api\Data\training_data_real.csv', 
                        help="Path to output training CSV.")
    return parser.parse_args()

def clean_ndvi_data(input_file):
    print("Loading raw GEE data...")
    
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}. "
                                "Check path and filename (e.g., 'ee-chart.csv' or 'nakuru_county_ndvi_avg.csv'). "
                                "If the file is from GEE export, it might be named 'nakuru_county_ndvi_avg.csv'.")
    
    # 1. Load Data
    df = pd.read_csv(input_file)
    
    # 2. Detect and Parse Date Column (Flexible for GEE export or chart download)
    if 'system:time_start' in df.columns:
        date_col = 'system:time_start'
        date_format = '%b %d, %Y'  # e.g., 'Jan 1, 2024' from chart
    elif 'date' in df.columns:
        date_col = 'date'
        date_format = '%Y-%m-%d'  # e.g., '2024-01-01' from export (fixed format string)
    else:
        raise KeyError("CSV must have either 'date' or 'system:time_start' column. "
                       "Preview the CSV to confirm columns.")
    
    df['date'] = pd.to_datetime(df[date_col], format=date_format, errors='coerce')
    if df['date'].isnull().any():
        raise ValueError("Invalid date format in CSV. Check data and try manual parsing if needed.")
    
    # Drop original date col if it was 'system:time_start'
    if date_col != 'date':
        df = df.drop(columns=[date_col])
    
    # 3. Handle Duplicate Dates (Group by date and average NDVI)
    df_daily = df.groupby('date')['ndvi'].mean().reset_index()
    
    # 4. Sort by Date
    df_daily = df_daily.sort_values('date')
    
    # 5. Clean Noise (Rolling Average, window=3)
    df_daily['ndvi_smooth'] = df_daily['ndvi'].rolling(window=3, min_periods=1).mean()
    
    # Preview Plot: Save to file (no display needed)
    plt.figure(figsize=(10, 5))
    plt.plot(df_daily['date'], df_daily['ndvi'], label='Raw NDVI', alpha=0.5)
    plt.plot(df_daily['date'], df_daily['ndvi_smooth'], label='Smoothed NDVI', linewidth=2)
    plt.title('NDVI Time Series')
    plt.xlabel('Date')
    plt.ylabel('NDVI')
    plt.legend()
    preview_path = os.path.join(os.path.dirname(input_file), 'ndvi_time_series_preview.png')
    plt.savefig(preview_path)
    plt.close()
    print(f"NDVI preview saved as: {preview_path}")
    
    print(f"Data cleaned. Reduced from {len(df)} raw rows to {len(df_daily)} daily records.")
    return df_daily

def generate_synthetic_yields(df_ndvi, num_samples=500):
    print("Generating synthetic ground truth data...")
    
    training_samples = []
    ndvi_values = df_ndvi['ndvi_smooth'].values
    series_length = len(ndvi_values)
    
    for field_id in range(1, num_samples + 1):
        # Simulate different "seasons/years" by random subsampling/shifting
        start_idx = random.randint(0, series_length - min(series_length // 2, series_length))
        sample_length = random.randint(series_length // 2, series_length)
        field_ndvi = ndvi_values[start_idx:start_idx + sample_length].copy()
        
        # Add per-point variation (Gaussian noise) for realism
        noise = np.random.normal(0, 0.05, len(field_ndvi))
        field_ndvi += noise
        field_ndvi = np.clip(field_ndvi, 0, 1)  # NDVI range [0,1]
        
        # Feature Engineering
        max_ndvi = field_ndvi.max()
        mean_ndvi = field_ndvi.mean()
        cumulative_ndvi = field_ndvi.sum()  # Better proxy for total biomass
        
        # Synthetic Yield: Non-linear + noise
        base_yield = 1000
        yield_boost = (np.sqrt(cumulative_ndvi) * 100) + random.uniform(-300, 300)
        yield_kg_ha = base_yield + yield_boost
        yield_kg_ha = max(500, min(yield_kg_ha, 5000))
        
        # Random year for variety
        year = random.randint(2015, 2024)
        
        training_samples.append({
            'field_id': field_id,
            'year': year,
            'ndvi_mean': round(mean_ndvi, 3),
            'ndvi_max': round(max_ndvi, 3),
            'ndvi_sum': round(cumulative_ndvi, 3),
            'yield_kg_ha': int(yield_kg_ha)  # Target variable
        })
        
    return pd.DataFrame(training_samples)

# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    args = parse_args()
    input_file = args.input
    output_file = args.output
    
    # 1. Clean the GEE Data
    clean_df = clean_ndvi_data(input_file)
    
    # 2. Create the Training Dataset
    final_df = generate_synthetic_yields(clean_df)
    
    # 3. Save to CSV
    final_df.to_csv(output_file, index=False)
    
    print("\nSUCCESS! ======================")
    print(f"Saved processed data to: {output_file}")
    print(f"Preview of data ready for ML:")
    print(final_df.head())
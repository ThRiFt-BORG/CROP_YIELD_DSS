import ee
import geemap
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# --- 1. INITIALIZATION AND BOUNDARY DEFINITION ---
try:
    ee.Initialize()
except Exception as e:
    print(f"GEE Initialization failed. Please run 'earthengine authenticate'. Error: {e}")
    exit()

# Define the Area of Interest (Nakuru County, Kenya)
# For simplicity, we will use a rough bounding box or a pre-defined GEE feature collection.
# For this example, we'll use a rough point and buffer.
NAKURU_CENTER = Point(36.07, -0.30) # Approximate center of Nakuru
NAKURU_BUFFER_KM = 50 # 50km radius for a large area
NAKURU_AOI = NAKURU_CENTER.buffer(NAKURU_BUFFER_KM / 111.32).envelope # Convert km to degrees

# Convert to GEE Geometry
nakuru_ee_geom = ee.Geometry.Polygon(list(NAKURU_AOI.exterior.coords))

# --- 2. DATA ACQUISITION PARAMETERS ---
START_DATE = '2020-01-01'
END_DATE = '2021-12-31'
SCALE = 30 # Resolution in meters (Sentinel-2 is 10m, but 30m is safer for large area)

# --- 3. SENTINEL-2 (NDVI) DATA EXTRACTION ---
def add_ndvi(image):
    """Calculates and adds the Normalized Difference Vegetation Index (NDVI)."""
    # Bands: B4 (Red), B8 (NIR)
    ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
    return image.addBands(ndvi)

s2_collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
    .filterDate(START_DATE, END_DATE) \
    .filterBounds(nakuru_ee_geom) \
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10)) \
    .map(add_ndvi)

# Function to extract time series for a single point
def extract_time_series_at_point(point_lon, point_lat, collection, band_name):
    point_ee = ee.Geometry.Point(point_lon, point_lat)
    
    # Extract values for the point
    data = collection.getRegion(point_ee, SCALE).getInfo()
    
    # Convert to Pandas DataFrame
    header = data[0]
    df = pd.DataFrame(data[1:], columns=header)
    
    # Filter for the band and clean up
    df = df[['time', band_name]]
    df = df.rename(columns={'time': 'date', band_name: band_name.lower()})
    df['date'] = pd.to_datetime(df['date'].str[:10])
    df = df.dropna()
    
    return df

# --- 4. ERA5-LAND (WEATHER) DATA EXTRACTION ---
# Example: Extracting 2m air temperature (t2m)
era5_collection = ee.ImageCollection('ECMWF/ERA5_LAND/HOURLY') \
    .filterDate(START_DATE, END_DATE) \
    .filterBounds(nakuru_ee_geom) \
    .select('temperature_2m')

# Function to extract weather data (requires aggregation, here we'll use monthly mean)
def extract_weather_data(collection, band_name):
    def monthly_mean(year, month):
        start = ee.Date.fromYMD(year, month, 1)
        end = start.advance(1, 'month')
        
        # Filter to the month and calculate mean
        mean_image = collection.filterDate(start, end).mean()
        
        # Extract mean value over the AOI
        stats = mean_image.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=nakuru_ee_geom,
            scale=SCALE
        )
        
        return ee.Feature(None, {
            'date': start.format('YYYY-MM-dd'),
            band_name: stats.get(band_name)
        })

    # Create a list of all year/month combinations
    dates = [
        (y, m) for y in range(2020, 2022) for m in range(1, 13)
    ]
    
    features = [monthly_mean(y, m) for y, m in dates]
    
    # Convert to FeatureCollection and then to Pandas DataFrame
    fc = ee.FeatureCollection(features)
    df = geemap.ee_to_pandas(fc)
    df = df.rename(columns={band_name: band_name.lower()})
    df['date'] = pd.to_datetime(df['date'])
    return df.dropna()

# --- 5. EXECUTION EXAMPLE ---
if __name__ == '__main__':
    # Example point (replace with your actual field coordinates)
    FIELD_LON, FIELD_LAT = 36.07, -0.30 
    
    print("--- 1. Extracting Sentinel-2 NDVI Time Series ---")
    ndvi_df = extract_time_series_at_point(FIELD_LON, FIELD_LAT, s2_collection, 'NDVI')
    print(f"NDVI Data Points: {len(ndvi_df)}")
    
    print("\n--- 2. Extracting ERA5 Temperature Data ---")
    temp_df = extract_weather_data(era5_collection, 'temperature_2m')
    print(f"Temperature Data Points: {len(temp_df)}")
    
    # Save the data for local processing and model training
    ndvi_df.to_csv('ndvi_time_series.csv', index=False)
    temp_df.to_csv('era5_temp_data.csv', index=False)
    
    print("\nData extraction complete. Files saved: ndvi_time_series.csv, era5_temp_data.csv")
    print("You can now use these files to update your train.py script.")

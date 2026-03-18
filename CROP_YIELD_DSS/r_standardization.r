# Load libraries
library(tidyverse)
library(sf)
library(terra)

# -------------------------------
# 1. Load tabular dataset
# -------------------------------
data <- read_csv("data/sample_agri_data.csv")

# Inspect
glimpse(data)

# -------------------------------
# 2. Basic cleaning
# -------------------------------
clean_data <- data %>%
  rename(
    county = County,
    yield = Yield_t_ha,
    rainfall = Rain_mm,
    temp = Temp_C
  ) %>%
  drop_na() %>%
  filter(yield > 0)

# -------------------------------
# 3. Feature engineering
# -------------------------------
clean_data <- clean_data %>%
  mutate(
    yield_class = case_when(
      yield < 2 ~ "Low",
      yield < 4 ~ "Medium",
      TRUE ~ "High"
    ),
    rain_temp_ratio = rainfall / temp
  )

# -------------------------------
# 4. Convert to spatial (sf)
# -------------------------------
# Assuming lat/lon columns exist
spatial_data <- st_as_sf(
  clean_data,
  coords = c("longitude", "latitude"),
  crs = 4326
)

# -------------------------------
# 5. Load boundary shapefile
# -------------------------------
counties <- st_read("data/kenya_counties.geojson")

# Spatial join (like PostGIS ST_Contains)
joined <- st_join(spatial_data, counties)

# -------------------------------
# 6. Export standardized dataset
# -------------------------------
write_csv(joined, "output/standardized_agri_data.csv")

st_write(joined, "output/standardized_agri_data.geojson", delete_dsn = TRUE)

# -------------------------------
# 7. Simple visualization
# -------------------------------
ggplot(joined) +
  geom_sf(aes(color = yield_class)) +
  labs(title = "Yield Classification Map")

# -------------------------------
# 8. Summary stats (Carob-style quick insight)
# -------------------------------
summary_stats <- joined %>%
  group_by(county) %>%
  summarise(
    avg_yield = mean(yield),
    avg_rainfall = mean(rainfall),
    avg_temp = mean(temp)
  )

write_csv(summary_stats, "output/county_summary.csv")

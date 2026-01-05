# ===============================
# Wheels builder
# ===============================
FROM crop-dss-base AS wheels

# Set GDAL environment variables for the build
ENV GDAL_CONFIG=/usr/bin/gdal-config \
    CPLUS_INCLUDE_PATH=/usr/include/gdal \
    C_INCLUDE_PATH=/usr/include/gdal

RUN python -m pip install --upgrade pip setuptools wheel

# PRE-INSTALL build dependencies manually with high timeout
RUN pip install --timeout 120 --retries 10 \
    "setuptools>=67.8" \
    "wheel" \
    "cython~=3.1.0" \
    "numpy>=2.0.0"

COPY geo-api/requirements.txt .

# Build wheels with isolation turned off
RUN pip wheel --no-cache-dir --wheel-dir=/wheels \
    --timeout 120 --retries 10 \
    --no-build-isolation \
    --no-binary rasterio \
    -r requirements.txt
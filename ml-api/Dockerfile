# ===============================
# Wheels builder
# ===============================
FROM crop-dss-base AS wheels

# 1. Set GDAL environment variables for the build
ENV GDAL_CONFIG=/usr/bin/gdal-config \
    CPLUS_INCLUDE_PATH=/usr/include/gdal \
    C_INCLUDE_PATH=/usr/include/gdal

RUN python -m pip install --upgrade pip setuptools wheel

# 2. PRE-INSTALL build dependencies manually with high timeout
# This ensures numpy and cython are ready BEFORE rasterio starts
RUN pip install --timeout 120 --retries 10 \
    "setuptools>=67.8" \
    "wheel" \
    "cython~=3.1.0" \
    "numpy>=2.0.0"

COPY ml-api/requirements.txt .

# 3. Build the wheels using --no-build-isolation
# This tells pip: "Use the numpy/cython I just installed, don't try to download them again"
RUN pip wheel --no-cache-dir --wheel-dir=/wheels \
    --timeout 120 --retries 10 \
    --no-build-isolation \
    --no-binary rasterio \
    -r requirements.txt
    
# ===============================
# Runtime image
# ===============================
FROM crop-dss-base

WORKDIR /app

COPY --from=wheels /wheels /wheels
COPY ml-api/requirements.txt .

# Install from local wheels (no internet needed here)
RUN pip install --no-index --find-links=/wheels -r requirements.txt

COPY ml-api .
COPY shared ./shared

ENV GUNICORN_WORKERS=2

CMD gunicorn main:app \
  --workers ${GUNICORN_WORKERS} \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
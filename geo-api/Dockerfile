# ===============================
# Stage 1: Wheels builder
# ===============================
FROM crop-dss-base AS wheels

# Set GDAL environment variables for the build
ENV GDAL_CONFIG=/usr/bin/gdal-config \
    CPLUS_INCLUDE_PATH=/usr/include/gdal \
    C_INCLUDE_PATH=/usr/include/gdal

RUN python -m pip install --upgrade pip setuptools wheel

# PRE-INSTALL build dependencies manually to avoid isolated network drops
RUN pip install --timeout 120 --retries 10 \
    "setuptools>=67.8" \
    "wheel" \
    "cython~=3.1.0" \
    "numpy>=2.0.0"

COPY geo-api/requirements.txt .

# Build the wheels
RUN pip wheel --no-cache-dir --wheel-dir=/wheels \
    --timeout 120 --retries 10 \
    --no-build-isolation \
    --no-binary rasterio \
    -r requirements.txt

# ===============================
# Stage 2: Runtime image
# ===============================
FROM crop-dss-base

WORKDIR /app

# Copy the built wheels from the first stage
COPY --from=wheels /wheels /wheels
COPY geo-api/requirements.txt .

# Install from local wheels (No internet needed)
RUN pip install --no-index --find-links=/wheels -r requirements.txt

# Copy the app code
COPY geo-api .
COPY shared ./shared

ENV GUNICORN_WORKERS=3

CMD gunicorn main:app \
  --workers ${GUNICORN_WORKERS} \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
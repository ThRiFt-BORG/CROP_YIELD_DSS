# ===============================
# Wheels builder
# ===============================
FROM crop-dss-base AS wheels

# Install Fortran compiler (Required for real DSSAT integration)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gfortran \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set GDAL environment variables for the build
ENV GDAL_CONFIG=/usr/bin/gdal-config \
    CPLUS_INCLUDE_PATH=/usr/include/gdal \
    C_INCLUDE_PATH=/usr/include/gdal

RUN python -m pip install --upgrade pip setuptools wheel

# PRE-INSTALL build dependencies 
RUN pip install --timeout 120 --retries 10 \
    "setuptools>=67.8" \
    "wheel" \
    "cython~=3.0.0" \
    "numpy>=2.0.0"

COPY ml_api/requirements.txt .

# Build the wheels including DSSATTools
RUN pip wheel --no-cache-dir --wheel-dir=/wheels \
    --timeout 120 --retries 10 \
    --no-build-isolation \
    --no-binary rasterio \
    -r requirements.txt
    
# ===============================
# Runtime image
# ===============================
FROM crop-dss-base

# Re-install gfortran in runtime image so the libraries can run
RUN apt-get update && apt-get install -y --no-install-recommends \
    gfortran \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=wheels /wheels /wheels
COPY ml_api/requirements.txt .

# Install from local wheels
RUN pip install --no-index --find-links=/wheels -r requirements.txt

COPY ml_api .
COPY shared ./shared

ENV GUNICORN_WORKERS=2

CMD gunicorn main:app \
  --workers ${GUNICORN_WORKERS} \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
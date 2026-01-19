# ===============================
# Stage 1: Wheels builder
# ===============================
FROM crop-dss-base AS wheels

# Install Fortran and Build tools for library compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    gfortran \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

ENV GDAL_CONFIG=/usr/bin/gdal-config

RUN python -m pip install --upgrade pip setuptools wheel

# Build-time dependencies for Python 3.12 compatibility
RUN pip install --timeout 1000 --retries 20 \
    "setuptools>=67.8" \
    "wheel" \
    "cython~=3.0.0" \
    "numpy>=2.0.0"

COPY ml_api/requirements.txt .

# Compile all requirements into wheels
RUN pip wheel --no-cache-dir --wheel-dir=/wheels \
    --timeout 1000 --retries 20 \
    -r requirements.txt

# ===============================
# Stage 2: Runtime image (The one that stays running)
# ===============================
FROM crop-dss-base

# 1. Install gfortran (Mandatory for DSSAT engine runtime)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gfortran \
    && rm -rf /var/lib/apt/lists/*

# 2. SHIELD: Create the temp workspace during the build
# This ensures it exists the millisecond Python imports the library
RUN mkdir -p /tmp/DSSAT048 && \
    touch /tmp/DSSAT048/DATA.CDE && \
    chmod -R 777 /tmp/DSSAT048

WORKDIR /app

# 3. Copy pre-compiled wheels from Stage 1
COPY --from=wheels /wheels /wheels
COPY ml_api/requirements.txt .

# 4. Install using the local wheels (No internet used here)
RUN pip install --no-index --find-links=/wheels -r requirements.txt

# 5. Copy your local code into the container
COPY ml_api .
COPY shared ./shared

ENV GUNICORN_WORKERS=2

# 6. Start the server
CMD ["gunicorn", "main:app", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
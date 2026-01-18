# ===============================
# Stage 1: Wheels builder
# ===============================
FROM crop-dss-base AS wheels

RUN apt-get update && apt-get install -y --no-install-recommends \
    gfortran build-essential && rm -rf /var/lib/apt/lists/*

ENV GDAL_CONFIG=/usr/bin/gdal-config
RUN python -m pip install --upgrade pip setuptools wheel

RUN pip install --timeout 1000 --retries 20 \
    "setuptools>=67.8" "wheel" "cython~=3.0.0" "numpy>=2.0.0"

COPY ml_api/requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir=/wheels --timeout 1000 --retries 20 -r requirements.txt

# ===============================
# Stage 2: Runtime image
# ===============================
FROM crop-dss-base

# Mandatory for DSSAT engine
RUN apt-get update && apt-get install -y --no-install-recommends \
    gfortran && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=wheels /wheels /wheels
COPY ml_api/requirements.txt .
RUN pip install --no-index --find-links=/wheels -r requirements.txt

COPY ml_api .
COPY shared ./shared

ENV GUNICORN_WORKERS=2
CMD ["gunicorn", "main:app", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
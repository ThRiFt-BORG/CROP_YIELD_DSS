# ===============================
# Stage 1: Wheels builder
# ===============================
FROM crop-dss-base AS wheels

ENV GDAL_CONFIG=/usr/bin/gdal-config \
    CPLUS_INCLUDE_PATH=/usr/include/gdal \
    C_INCLUDE_PATH=/usr/include/gdal

RUN python -m pip install --upgrade pip setuptools wheel

# Mega-timeout for slow connection
RUN pip install --timeout 1000 --retries 20 \
    "setuptools>=67.8" \
    "wheel" \
    "cython~=3.0.0" \
    "numpy>=2.0.0"

COPY geo_api/requirements.txt .

# Building wheels (Allowing binaries for speed)
RUN pip wheel --no-cache-dir --wheel-dir=/wheels \
    --timeout 1000 --retries 20 \
    -r requirements.txt

# ===============================
# Stage 2: Runtime image
# ===============================
FROM crop-dss-base

WORKDIR /app

COPY --from=wheels /wheels /wheels
COPY geo_api/requirements.txt .

RUN pip install --no-index --find-links=/wheels -r requirements.txt

COPY geo_api .
COPY shared ./shared

ENV GUNICORN_WORKERS=3
CMD ["gunicorn", "main:app", "--workers", "3", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
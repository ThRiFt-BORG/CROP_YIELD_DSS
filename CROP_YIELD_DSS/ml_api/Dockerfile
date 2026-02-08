# ===============================
# Stage 1: Wheels builder
# ===============================
FROM crop-dss-base AS wheels

# FIX: Bypass network interception by forcing a reliable mirror
RUN echo "deb http://deb.debian.org/debian bookworm main" > /etc/apt/sources.list && \
    echo "deb http://deb.debian.org/debian bookworm-updates main" >> /etc/apt/sources.list && \
    echo "deb http://security.debian.org/debian-security bookworm-security main" >> /etc/apt/sources.list

RUN apt-get -o Acquire::Retries=5 update && apt-get install -y --no-install-recommends \
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

RUN echo "deb http://deb.debian.org/debian bookworm main" > /etc/apt/sources.list && \
    apt-get -o Acquire::Retries=5 update && apt-get install -y --no-install-recommends \
    gfortran && rm -rf /var/lib/apt/lists/*

# SHIELD: Create workspace during build to prevent FileNotFoundError
RUN mkdir -p /tmp/DSSAT048 && \
    touch /tmp/DSSAT048/DATA.CDE && \
    chmod -R 777 /tmp/DSSAT048

WORKDIR /app
COPY --from=wheels /wheels /wheels
COPY ml_api/requirements.txt .
RUN pip install --no-index --find-links=/wheels -r requirements.txt

COPY ml_api .
COPY shared ./shared

ENV GUNICORN_WORKERS=1
CMD ["gunicorn", "main:app", "--workers", "1", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--timeout", "300"]
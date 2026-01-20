# ===============================
# Stage 1: Wheels builder
# ===============================
FROM crop-dss-base AS wheels
RUN python -m pip install --upgrade pip setuptools wheel
RUN pip install --timeout 1000 --retries 20 "setuptools>=67.8" "wheel" "cython~=3.0.0" "numpy>=2.0.0"

COPY dis/requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir=/wheels --timeout 1000 --retries 20 -r requirements.txt

# ===============================
# Stage 2: Runtime image
# ===============================
FROM crop-dss-base
WORKDIR /app
COPY --from=wheels /wheels /wheels
COPY dis/requirements.txt .
RUN pip install --no-index --find-links=/wheels -r requirements.txt
COPY dis .
COPY shared ./shared

# FIX: Added missing comma and separated --timeout from 600
CMD ["gunicorn", "main:app", "--workers", "1", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--timeout", "600"]
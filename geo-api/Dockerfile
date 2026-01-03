# Use a Python base image suitable for geospatial libraries
FROM python:3.11-slim

# Install system dependencies for geospatial libraries (GDAL, GEOS, PROJ)
# and MySQL client library
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    gdal-bin \
    proj-bin \
    libmariadb-dev && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY geo-api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY geo-api .
COPY shared /app/shared

# Expose the port the application runs on
EXPOSE 8000

# Command to run the application
CMD ["gunicorn", "main:app", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]

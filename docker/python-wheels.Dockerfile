FROM crop-python-geo-base:latest

WORKDIR /wheels

# Upgrade build tooling
RUN python -m pip install --upgrade pip setuptools wheel

# Prebuild all required wheels (once)
RUN pip wheel \
    numpy \
    scipy \
    pandas \
    joblib \
    scikit-learn \
    shapely \
    rasterio \
    geopandas \
    Pillow \
    fastapi \
    uvicorn \
    gunicorn \
    rio-tiler \
    pystac-client \
    requests \
    boto3 \
    sqlalchemy \
    pymysql \
    psycopg2-binary \
    geoalchemy2 \
    -w /wheels
# The wheels will be stored in /wheels for reuse in other images
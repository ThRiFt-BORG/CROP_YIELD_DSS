FROM crop-python-geo-base:latest

# ---------------------------
# Build wheels only once
# ---------------------------
WORKDIR /wheels

RUN python -m pip install --upgrade pip wheel setuptools

# Precompile heavy scientific stack
RUN pip wheel \
    numpy \
    scipy \
    pandas \
    scikit-learn \
    shapely \
    rasterio \
    -w /wheels

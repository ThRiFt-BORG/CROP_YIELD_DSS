from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from geo_api.app.routers.geo_router import router as geo_router
import os

# Initialize FastAPI app
app = FastAPI(
    title="Geo-API",
    description="Spatial queries, raster access, and ML orchestration for the DSS.",
    version="1.0.0"
)

# CORS Configuration (for local development and frontend communication)
origins = [
    "http://localhost:3000",  # Frontend development server
    os.getenv("FRONTEND_URL", "*") # Production frontend URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the main router
app.include_router(geo_router, prefix="/v1")

@app.get("/")
def read_root():
    return {"message": "Geo-API is running"}

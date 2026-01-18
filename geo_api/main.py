from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.geo_router import router as geo_router
import os

app = FastAPI(
    title="geo_api",
    description="Spatial queries, raster access, and ML orchestration.",
    version="1.0.0"
)

# Robust CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(geo_router, prefix="/v1")

# Added for Frontend Badge status check
@app.get("/v1/status")
def get_status():
    return {"status": "healthy", "service": "geo_api"}

@app.get("/")
def read_root():
    return {"message": "geo_api is running"}
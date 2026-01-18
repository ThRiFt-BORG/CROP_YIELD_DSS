import os
import pathlib
import logging

# =================================================================
# DEFINITIVE RUNTIME FIX FOR DSSATTools v3.0.0 (ISO Robustness)
# This MUST run before any other imports to prevent the /tmp crash.
# =================================================================
try:
    tmp_dir = pathlib.Path('/tmp/DSSAT048')
    tmp_dir.mkdir(parents=True, exist_ok=True)
    # The library tries to remove this file on import. We create it so it can succeed.
    (tmp_dir / 'DATA.CDE').touch()
    # Set permissions so the Fortran engine can write results
    os.system('chmod -R 777 /tmp/DSSAT048')
    print("DSSAT Runtime Workspace Initialized Successfully.")
except Exception as e:
    print(f"Warning: DSSAT Workspace setup failed: {e}")

# Now we can safely import the rest of the app
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prediction import router as prediction_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ml_api", version="1.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prediction_router, prefix="/v1")

@app.get("/health")
@app.get("/v1/status")
async def health():
    return {"status": "ready", "engine": "DSSAT v3.0.0"}
import os
import pathlib
import logging

# Set up logging early
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Shield 2: Robust Runtime Initialization
def init_dssat_workspace():
    try:
        tmp_dir = pathlib.Path('/tmp/DSSAT048')
        tmp_dir.mkdir(parents=True, exist_ok=True)
        flag_file = tmp_dir / 'DATA.CDE'
        if not flag_file.exists():
            flag_file.touch()
        os.system('chmod -R 777 /tmp/DSSAT048')
        logger.info("DSSAT Runtime Workspace Verified.")
    except Exception as e:
        logger.error(f"Workspace setup failed: {e}")

init_dssat_workspace()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="ml_api", version="1.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DELAYED IMPORT: This prevents the library from importing 
# before the workspace is guaranteed to be ready.
from prediction import router as prediction_router
app.include_router(prediction_router, prefix="/v1")

@app.get("/health")
@app.get("/v1/status")
async def health():
    return {"status": "ready", "engine": "DSSAT v3.0.0"}
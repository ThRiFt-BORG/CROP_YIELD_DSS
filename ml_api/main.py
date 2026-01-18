from fastapi import FastAPI
from prediction import router as prediction_router
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="ml_api", version="1.2.0")

# This includes all the logic from prediction.py
app.include_router(prediction_router, prefix="/v1")

@app.get("/health")
async def health():
    return {"status": "ready"}
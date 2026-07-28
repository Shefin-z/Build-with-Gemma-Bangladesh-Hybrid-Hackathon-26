"""FastAPI endpoint used by the Board2Learn React experience."""

from __future__ import annotations

import asyncio
import os
from io import BytesIO

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, UnidentifiedImageError

from gemma_service import analyze_whiteboard


app = FastAPI(title="Board2Learn BD API", version="1.0.0")
allowed_origins = os.getenv(
    "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPPORTED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_BYTES = 10 * 1024 * 1024


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "board2learn-bd"}


@app.post("/api/extract")
async def extract(file: UploadFile = File(...)) -> dict:
    """Analyse one board image and return the validated study-guide JSON."""
    if file.content_type not in SUPPORTED_IMAGE_TYPES:
        raise HTTPException(status_code=415, detail="Only JPG, PNG and WEBP images are supported.")

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="The uploaded image is empty.")
    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="Image must be smaller than 10 MB.")

    try:
        image = Image.open(BytesIO(image_bytes))
        image.load()
    except (UnidentifiedImageError, OSError) as error:
        raise HTTPException(status_code=400, detail="The file could not be read as an image.") from error

    guide = await asyncio.to_thread(analyze_whiteboard, image)
    if guide.title == "Image analysis failed":
        detail = guide.unclear_sections[0] if guide.unclear_sections else "Vision analysis failed."
        raise HTTPException(status_code=502, detail=detail)
    return guide.model_dump()

import os
from io import BytesIO
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, UnidentifiedImageError

app = FastAPI(title="FluxSwap Backend", version="0.1.0")

# For a public prototype. In production, restrict this to your exact GitHub Pages origin.
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins if origin.strip()],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

MAX_BYTES = 8 * 1024 * 1024  # 8 MB per image
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}

@app.get("/")
def root():
    return {
        "name": "FluxSwap Backend",
        "status": "online",
        "note": "API foundation only; no AI face-swap model is connected yet."
    }

@app.get("/health")
def health():
    return {"ok": True}

async def validate_image(upload: UploadFile, label: str) -> dict:
    if upload.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail=f"{label} must be JPG, PNG, or WEBP.")
    data = await upload.read(MAX_BYTES + 1)
    if not data:
        raise HTTPException(status_code=400, detail=f"{label} is empty.")
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail=f"{label} is larger than 8 MB.")
    try:
        image = Image.open(BytesIO(data))
        image.verify()
        # Re-open after verify to read dimensions safely.
        image = Image.open(BytesIO(data))
        width, height = image.size
    except (UnidentifiedImageError, OSError, ValueError):
        raise HTTPException(status_code=400, detail=f"{label} is not a valid image.")
    return {"filename": upload.filename or label, "width": width, "height": height, "bytes": len(data)}

@app.post("/api/morph-preview")
async def morph_preview(
    source_face: UploadFile = File(...),
    target_image: UploadFile = File(...)
):
    source = await validate_image(source_face, "Source face")
    target = await validate_image(target_image, "Target image")
    # This is deliberately a status endpoint, not a fake AI result.
    # Connect a licensed/appropriate model here before claiming a real swap.
    return {
        "ok": True,
        "stage": "images_validated",
        "message": "Both images are valid. No AI face-swap model is connected yet.",
        "source_face": source,
        "target_image": target
    }

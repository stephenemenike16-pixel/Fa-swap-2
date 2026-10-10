import os
from io import BytesIO
from tempfile import NamedTemporaryFile
from pathlib import Path

import replicate
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from PIL import Image, UnidentifiedImageError

app = FastAPI(title="FluxSwap Backend", version="0.2.0")

# Set ALLOWED_ORIGINS in Render to your exact GitHub Pages origin before public use.
# Example: https://YOUR-USERNAME.github.io
allowed_origins = [x.strip() for x in os.getenv("ALLOWED_ORIGINS", "*").split(",") if x.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

MAX_BYTES = 8 * 1024 * 1024
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MODEL_VERSION = "codeplugtech/face-swap:278a81e7ebb22db98bcba54de985d22cc1abeead2754eb1f2af717247be69b34"

@app.get("/")
def root():
    configured = bool(os.getenv("REPLICATE_API_TOKEN"))
    return {
        "name": "FluxSwap Backend",
        "status": "online",
        "ai_configured": configured,
        "note": "AI processing is configured." if configured else "Add REPLICATE_API_TOKEN in Render environment variables to enable AI processing."
    }

@app.get("/health")
def health():
    return {"ok": True, "ai_configured": bool(os.getenv("REPLICATE_API_TOKEN"))}

async def read_and_validate(upload: UploadFile, label: str) -> bytes:
    if upload.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail=f"{label} must be JPG, PNG, or WEBP.")
    data = await upload.read(MAX_BYTES + 1)
    if not data:
        raise HTTPException(status_code=400, detail=f"{label} is empty.")
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail=f"{label} must be 8 MB or smaller.")
    try:
        im = Image.open(BytesIO(data))
        im.verify()
    except (UnidentifiedImageError, OSError, ValueError):
        raise HTTPException(status_code=400, detail=f"{label} is not a valid image.")
    return data

@app.post("/api/morph-preview")
async def morph_preview(
    source_face: UploadFile = File(...),
    target_image: UploadFile = File(...),
    consent_confirmed: bool = Form(...),
):
    """Runs a face swap through Replicate. Only submit images you own or have permission to edit."""
    if not consent_confirmed:
        raise HTTPException(status_code=400, detail="Please confirm you have permission to use both images.")
    if not os.getenv("REPLICATE_API_TOKEN"):
        raise HTTPException(status_code=503, detail="AI is not configured yet. Add REPLICATE_API_TOKEN in Render Environment Variables.")

    source_bytes = await read_and_validate(source_face, "Source face")
    target_bytes = await read_and_validate(target_image, "Target image")

    # Replicate accepts file handles; temporary files avoid exposing image data in public URLs.
    try:
        with NamedTemporaryFile(suffix=".jpg") as source_file, NamedTemporaryFile(suffix=".jpg") as target_file:
            source_file.write(source_bytes)
            source_file.flush()
            target_file.write(target_bytes)
            target_file.flush()
            with open(source_file.name, "rb") as source_handle, open(target_file.name, "rb") as target_handle:
                result = replicate.run(
                    MODEL_VERSION,
                    input={"swap_image": source_handle, "input_image": target_handle},
                )
                # Replicate's model returns a file output or URL-like file object.
                if hasattr(result, "read"):
                    output_bytes = result.read()
                elif isinstance(result, (list, tuple)) and result:
                    item = result[0]
                    if hasattr(item, "read"):
                        output_bytes = item.read()
                    else:
                        raise RuntimeError("The model returned an unexpected output format.")
                else:
                    raise RuntimeError("The model returned an unexpected output format.")
    except HTTPException:
        raise
    except Exception as exc:
        # Do not expose provider internals, tokens, or uploaded image data to clients.
        raise HTTPException(status_code=502, detail="AI processing failed. Check the Render logs and your model-provider account.") from exc

    return Response(content=output_bytes, media_type="image/jpeg", headers={"Cache-Control": "no-store"})

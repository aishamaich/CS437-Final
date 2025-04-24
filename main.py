from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse
from pathlib import Path

app = FastAPI()

async def get_image():
    image_path = Path("winston.gif")

    if not image_path.is_file():
        return {"error": "image not found"}

    with image_path.open("rb") as winton:
        img_bytes = winton.read()
    imgio = BytesIO(img_bytes)
    imgio.seek(0)
    return StreamingResponse(content=imgio, media_type="image/gif")
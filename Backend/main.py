from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import uvicorn
import asyncio

# For the SunFounder Controller to work on your Raspberry Pi, you need to clone the SunfounderController repo: https://github.com/sunfounder/sunfounder-controller
from sunfounder_controller import SunFounderController
from picarx import Picarx
from vilib import Vilib
from time import sleep

# init SunFounder Controller class
sc = SunFounderController()
sc.set_name('Picarx-001')
sc.set_type('Picarx')
sc.start()

WIFI_HOST = "192.168.10.186"   # Change your own Raspberry Pi IP address

# The line below allows the server to send video to the front-end that can then be displayed in an iframe
sc.set('video','http://'+WIFI_HOST+':9000/mjpg')

Vilib.camera_start(vflip=False,hflip=False)
Vilib.show_fps()
Vilib.display(local=True, web=True)
Vilib.object_detect_set_model(path='/opt/vilib/detect.tflite')
Vilib.object_detect_set_labels(path='/opt/vilib/coco_labels.txt')
Vilib.object_detect_switch(True)

async def detectDogs():
    while True:
        if (Vilib.object_detection_list_parameter is not None and len(Vilib.object_detection_list_parameter) > 0):
            first_object = Vilib.object_detection_list_parameter[0]
            object_type = first_object.get('class_name')
            yield(f"data: {object_type}\n\n")
        await asyncio.sleep(0.5)
        
px = Picarx()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)
@app.options("/detections")
async def get_detection_options():
    return Response(status_code=200)
@app.post("/detections")
async def get_detections():
    return StreamingResponse(content=detectDogs(), media_type="text/event-stream")
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
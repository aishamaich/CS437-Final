from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse
from pathlib import Path

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

WIFI_HOST = "10.0.0.207"   # Change your own Raspberry Pi IP address
WIFI_PORT = 65432          # Port to listen on (non-privileged ports are > 1023)

# The line below allows the server to send video to the front-end that can then be displayed in an iframe
sc.set('video','http://'+WIFI_HOST+':9000/mjpg')

Vilib.camera_start(vflip=False,hflip=False)
Vilib.show_fps()
Vilib.display(local=True, web=True)
Vilib.object_detect_set_model(path='/opt/vilib/detect.tflite')
Vilib.object_detect_set_labels(path='/opt/vilib/coco_labels.txt')
Vilib.object_detect_switch(True)

def detectDogs():
    while True:
        if (Vilib.object_detection_list_parameter is not None and len(Vilib.object_detection_list_parameter) > 0):
            first_object = Vilib.object_detection_list_parameter[0]
            object_type = first_object.get('class_name')
            if (object_type == 'dog' or object_type == 'cat'):
                # If the object type we see here is a dog (or a cat, my husky was identified as a cat), then we need to send a message to the front-end over our server's socket connection
                print(object_type)
        sleep(1)
        
px = Picarx()

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
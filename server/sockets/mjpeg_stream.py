# drone_fire_fighting/server/sockets/mjpeg_stream.py
import asyncio
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import StreamingResponse
import cv2
import numpy as np

router = APIRouter()

latest_frame = None
lock = asyncio.Lock()


@router.post("/video/upload")
async def upload_frame(file: UploadFile = File(...)):
    """
    Drone sends JPEG images here via multipart/form-data.
    """
    global latest_frame
    content = await file.read()
    async with lock:
        latest_frame = content
    return {"status": "ok"}


async def mjpeg_generator():
    """
    MJPEG generator for browser.
    Continuously re-encodes the latest_frame to ensure proper JPEG.
    """
    global latest_frame

    while True:
        async with lock:
            frame_bytes = latest_frame

        if frame_bytes is not None:
            # Decode JPEG bytes to numpy
            np_arr = np.frombuffer(frame_bytes, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            if frame is None:
                # fallback black
                frame = np.zeros((480, 640, 3), dtype=np.uint8)

            # Resize to 480p
            frame = cv2.resize(frame, (640, 480))

            # Re-encode as JPEG
            _, jpeg = cv2.imencode(".jpg", frame)
            frame_bytes = jpeg.tobytes()
        else:
            # initial black frame
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            _, jpeg = cv2.imencode(".jpg", frame)
            frame_bytes = jpeg.tobytes()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" +
            frame_bytes +
            b"\r\n"
        )

        await asyncio.sleep(0.03)

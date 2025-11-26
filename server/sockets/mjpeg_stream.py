# drone_fire_fighting/server/sockets/mjpeg_stream.py

import asyncio
from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter()

# Store latest frame + event per drone
DRONE_FRAMES = {}       # drone_id → jpeg bytes
DRONE_EVENTS = {}       # drone_id → asyncio.Event()
DRONE_LOCKS = {}        # drone_id → asyncio.Lock()


def get_lock(drone_id: str):
    """Return an existing lock or create one."""
    if drone_id not in DRONE_LOCKS:
        DRONE_LOCKS[drone_id] = asyncio.Lock()
    return DRONE_LOCKS[drone_id]


def get_event(drone_id: str):
    """Return an existing event or create one."""
    if drone_id not in DRONE_EVENTS:
        DRONE_EVENTS[drone_id] = asyncio.Event()
    return DRONE_EVENTS[drone_id]


# ------------- Upload Route ----------------

@router.post("/video/upload/{drone_id}")
async def upload_frame(drone_id: str, file: UploadFile = File(...)):
    """
    Drone sends frames here.
    Each drone has its own buffer + event mechanism.
    """
    content = await file.read()
    if not content:
        raise HTTPException(400, "Empty frame received")

    async with get_lock(drone_id):
        DRONE_FRAMES[drone_id] = content
        get_event(drone_id).set()     # Wake the MJPEG generator

    return {"status": "ok"}


# ------------- MJPEG Stream Generator ----------------

async def mjpeg_generator(drone_id: str):
    """
    Independent MJPEG generator for each drone.
    """
    event = get_event(drone_id)

    while True:
        # Wait until a new frame arrives
        await event.wait()
        event.clear()

        frame_bytes = DRONE_FRAMES.get(drone_id)
        if not frame_bytes:
            continue

        # Directly yield the raw JPEG (no decoding/re-encoding)
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" +
            frame_bytes +
            b"\r\n"
        )

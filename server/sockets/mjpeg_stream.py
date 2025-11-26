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


# ------------- UDP server for drone frames ----------------

async def udp_frame_server(host="0.0.0.0", port=9999):
    print(f"🚀 UDP server listening on {host}:{port}")

    loop = asyncio.get_event_loop()
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: UDPFrameProtocol(),
        local_addr=(host, port)
    )


class UDPFrameProtocol(asyncio.DatagramProtocol):
    def datagram_received(self, data, addr):
        """
        Expected packet format:
        drone_id|JPEG_BYTES
        """
        try:
            drone_id, jpeg = data.split(b"|", 1)
            drone_id = drone_id.decode("utf-8")
        except Exception:
            print("❌ Bad UDP frame packet \n")
            
            return

        asyncio.create_task(self.store_frame(drone_id, jpeg))

    async def store_frame(self, drone_id, jpeg):
        async with get_lock(drone_id):
            DRONE_FRAMES[drone_id] = jpeg
            get_event(drone_id).set()


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

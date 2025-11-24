# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from sockets.drone_ws import router as drone_router
from sockets.mjpeg_stream import router as mjpeg_router, mjpeg_generator
from sockets.mjpeg_stream import mjpeg_generator

app = FastAPI(title="Firefighting Drone Server")

# CORS (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include your WebSocket routers
app.include_router(drone_router)
app.include_router(mjpeg_router)# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from sockets.mjpeg_stream import router as mjpeg_router, mjpeg_generator

app = FastAPI(title="Firefighting Drone Server")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MJPEG router
app.include_router(mjpeg_router)


@app.get("/video/stream")
async def video_stream():
    """
    MJPEG stream endpoint for browser.
    """
    return StreamingResponse(
        mjpeg_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame",
        headers={
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }
    )


@app.get("/")
async def root():
    return {"status": "ok", "message": "Firefighting Drone Server running"}


# MJPEG video route
@app.get("/video/stream")
async def video_stream():
    return StreamingResponse(
        mjpeg_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

# Simple health check
@app.get("/")
async def root():
    return {"status": "ok", "message": "Firefighting Drone Server running"}

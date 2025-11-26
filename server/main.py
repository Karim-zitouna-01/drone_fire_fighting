# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from sockets.drone_ws import router as drone_router
from sockets.mjpeg_stream import router as mjpeg_router, mjpeg_generator

app = FastAPI(title="Firefighting Drone Server")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Dev mode, adjust later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(drone_router)
app.include_router(mjpeg_router)


# ----------- New Multi-Drone Stream Route -------------

@app.get("/video/stream/{drone_id}")
async def video_stream(drone_id: str):
    """
    User selects the drone to stream.
    Each drone has a fully independent mjpeg generator.
    """
    return StreamingResponse(
        mjpeg_generator(drone_id),
        media_type="multipart/x-mixed-replace; boundary=frame",
        headers={
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        }
    )


@app.get("/")
async def root():
    return {"status": "ok", "message": "Firefighting Drone Server is running"}

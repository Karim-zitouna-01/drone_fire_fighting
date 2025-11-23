# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sockets.drone_ws import router as drone_router
from sockets.dashboard_ws import router as dashboard_router

app = FastAPI(title="Firefighting Drone Server")

# Optional: allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in production: set your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include WebSocket routers
app.include_router(drone_router)
app.include_router(dashboard_router)

# Simple health check
@app.get("/")
async def root():
    return {"status": "ok", "message": "Firefighting Drone Server running"}
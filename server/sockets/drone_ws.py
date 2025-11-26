# sockets/drone_ws.py

import base64
import json
import asyncio
from fastapi import APIRouter, WebSocket
from sockets.manager import ConnectionManager

from services.img_interpreter import ImgInterpreter
from services.data_interpreter import DataInterpreter
from services.danger_estimator import DangerEstimator

from storage.db import add_entry, get_last_entries


router = APIRouter()
manager = ConnectionManager()


async def process_frame_background(drone_id, image_b64, sensors, people_count, position):
    """
    Runs ALL heavy logic in a separate thread:
    - decode image
    - run VLM/LLM
    - compute danger
    - write DB
    - broadcast to dashboards
    """

    loop = asyncio.get_running_loop()

    def blocking_work():
        # Save image
        image_path = f"/tmp/{drone_id}.jpg"
        with open(image_path, "wb") as f:
            f.write(base64.b64decode(image_b64))

        # Heavy computations
        img_info = ImgInterpreter.interpret_image(image_path)
        data_info = DataInterpreter.interpret_data(
            sensors["temperature"],
            sensors["co2"]
        )
        danger = DangerEstimator.estimate_danger(
            img_info,
            data_info,
            people_count
        )

        # DB entry
        db_entry = {
            "image": image_b64,
            "img_info": img_info,
            "data_info": data_info,
            "people_count": people_count,
            "position": position,
            "danger": danger,
            "timestamp": __import__('time').time()
        }

        add_entry(drone_id, db_entry)

        return db_entry

    # Run heavy work in thread
    db_entry = await loop.run_in_executor(None, blocking_work)

    # Now broadcast (non-blocking)
    recent = get_last_entries(drone_id, 10)

    packet = {
        "type": "history_update",
        "drone_id": drone_id,
        "history": recent
    }

    await manager.broadcast_to_dashboards(packet)


@router.websocket("/ws/drone/{drone_id}")
async def drone_ws(websocket: WebSocket, drone_id: str):
    await manager.connect_drone(drone_id, websocket)

    try:
        while True:
            msg = await websocket.receive_text()
            data = json.loads(msg)

            if data["type"] == "frame":

                # Extract values
                image_b64 = data["image"]
                sensors = data["sensors"]
                people_count = data["people_count"]
                position = data["position"]

                # 🟢 Schedule background task (non-blocking!)
                asyncio.create_task(
                    process_frame_background(
                        drone_id, image_b64, sensors, people_count, position
                    )
                )

                # Keep WebSocket responsive
                await websocket.send_text("ACK")

    except Exception as e:
        print(f"Drone {drone_id} disconnected:", e)
        await manager.disconnect_drone(drone_id)

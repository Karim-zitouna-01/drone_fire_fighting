# sockets/drone_ws.py

import base64
import json
from fastapi import APIRouter, WebSocket
from sockets.manager import ConnectionManager

from services.img_interpreter import ImgInterpreter
from services.data_interpreter import DataInterpreter
from services.danger_estimator import DangerEstimator


router = APIRouter()
manager = ConnectionManager()


@router.websocket("/ws/drone/{drone_id}")
async def drone_ws(websocket: WebSocket, drone_id: str):
    await manager.connect_drone(drone_id, websocket)

    try:
        while True:
            msg = await websocket.receive_text()
            data = json.loads(msg)

            # ------------ Only expecting type=frame for now ------------
            if data["type"] == "frame":

                # === 1. Process image ===
                image_b64 = data["image"]
                sensors = data["sensors"]
                dist = data["distance_fire"]

                # Save image temporarily for VLM
                image_path = f"/tmp/{drone_id}.jpg"
                with open(image_path, "wb") as f:
                    f.write(base64.b64decode(image_b64))

                img_info = ImgInterpreter.interpret_image(image_path)
                data_info = DataInterpreter.interpret_data(
                    sensors["temperature"],
                    sensors["co2"],
                    dist
                )
                danger = DangerEstimator.estimate_danger(
                    img_info,
                    data_info,
                    img_info["people_count"]
                )

                # ------ Send results to DASHBOARDS ------
                dashboard_packet = {
                    "from": drone_id,
                    "type": "analysis",
                    "image": image_b64,
                    "img_info": img_info,
                    "data_info": data_info,
                    "danger": danger
                }
                await manager.broadcast_to_dashboards(dashboard_packet)

    except Exception as e:
        print(f"Drone {drone_id} disconnected:", e)
        await manager.disconnect_drone(drone_id)

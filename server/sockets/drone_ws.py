# sockets/drone_ws.py

import base64
import json
from fastapi import APIRouter, WebSocket
from sockets.manager import ConnectionManager

from services.img_interpreter import ImgInterpreter
from services.data_interpreter import DataInterpreter
from services.danger_estimator import DangerEstimator

from storage.db import add_entry, get_last_entries


router = APIRouter()
manager = ConnectionManager()


@router.websocket("/ws/drone/{drone_id}")
async def drone_ws(websocket: WebSocket, drone_id: str):
    await manager.connect_drone(drone_id, websocket)

    try:
        while True:
            msg = await websocket.receive_text()
            data = json.loads(msg)

            if data["type"] == "frame":

                image_b64 = data["image"]
                sensors = data["sensors"]
                people_count = data["people_count"]
                position = data["position"]
                # save image temporarily
                image_path = f"/tmp/{drone_id}.jpg"
                with open(image_path, "wb") as f:
                    f.write(base64.b64decode(image_b64))

                # analyze
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

                # === SAVE ENTRY TO DB ===
                db_entry = {
                    "image": image_b64,
                    "img_info": img_info,
                    "data_info": data_info,
                    "people_count": people_count,
                    "position": position,
                    "danger": danger,
                    "timestamp": __import__('time').time()
                }
                print("----"*10)
                print("New DB entry for drone", drone_id)
                print(db_entry["img_info"])
                
                print(db_entry["danger"])
                print("----"*10)
                add_entry(drone_id, db_entry)
            

                # === SEND LAST 10 ENTRIES TO DASHBOARDS ===
                recent = get_last_entries(drone_id, 10)

                packet = {
                    "type": "history_update",
                    "drone_id": drone_id,
                    "history": recent
                }

                await manager.broadcast_to_dashboards(packet)

    except Exception as e:
        print(f"Drone {drone_id} disconnected:", e)
        await manager.disconnect_drone(drone_id)

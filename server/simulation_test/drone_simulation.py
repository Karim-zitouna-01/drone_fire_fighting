# simulate_drone.py

import asyncio
import websockets
import base64
import json

DRONE_ID = "drone_test"
SERVER_URL = f"ws://localhost:8000/ws/drone/{DRONE_ID}"
IMAGE_PATH = "./test_img/6.jpg"

# Example sensor data
SENSOR_DATA = {
    "temperature": 35.5,
    "co2": 420
}

# Example drone position
DRONE_POSITION = {
    "gps_lat": 36.8065,
    "gps_lon": 10.1815,
    "altitude": 52.3   # meters
}

PEOPLE_COUNT = 3



async def send_frame():
    async with websockets.connect(SERVER_URL) as ws:

        # Read image and convert to base64
        with open(IMAGE_PATH, "rb") as f:
            image_bytes = f.read()
            image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        payload = {
            "type": "frame",
            "image": image_b64,
            "sensors": SENSOR_DATA,
            "people_count": PEOPLE_COUNT,
            "position": DRONE_POSITION,
            
        }

        print("Sending frame...")

        await ws.send(json.dumps(payload))
        print("Frame sent!")

        # keep connection alive
        while True:
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(send_frame())

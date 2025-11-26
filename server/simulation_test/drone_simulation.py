# simulation_test/drone_simulation.py

import asyncio
import os
import random
import cv2
import aiohttp
import websockets
import base64
import json

SERVER_UPLOAD_URL = "http://localhost:8000/video/upload/2"
TEST_IMG_FOLDER = "./test_img"


DRONE_ID = "2"

WS_FRAME_URL = f"ws://localhost:8000/ws/drone/{DRONE_ID}"
WS_STREAM_URL = f"ws://localhost:8000/video/stream"

TEST_IMG_FOLDER = "./test_img"


# ---------------------------
# Generate random sensor data
# ---------------------------
def generate_sensor_data():
    return {
        "temperature": round(random.uniform(25.0, 60.0), 2),
        "co2": random.randint(300, 900),
    }


def generate_position():
    return {
        "gps_lat": 36.8065 + random.uniform(-0.0005, 0.0005),
        "gps_lon": 10.1815 + random.uniform(-0.0005, 0.0005),
        "altitude": round(random.uniform(40, 70), 2),
    }


# ---------------------------
# TASK 1 → Send image+data every 20 sec
# ---------------------------
async def send_periodic_frames():
    print("📡 Starting periodic frame sender...")

    image_files = [
        f for f in os.listdir(TEST_IMG_FOLDER) 
        if f.lower().endswith((".jpg", ".png", ".jpeg"))
    ]

    if not image_files:
        print("❌ No images in test_img folder!")
        return

    async with websockets.connect(WS_FRAME_URL) as ws:
        print("✅ Connected to WS for frames.")

        while True:
            # pick random image
            img_name = random.choice(image_files)
            img_path = os.path.join(TEST_IMG_FOLDER, img_name)

            with open(img_path, "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode("utf-8")

            payload = {
                "type": "frame",
                "image": img_b64,
                "sensors": generate_sensor_data(),
                "people_count": random.randint(0, 10),
                "position": generate_position(),
            }

            print(f"📤 Sending frame: {img_name}")

            await ws.send(json.dumps(payload))

            await asyncio.sleep(20)  # every 20 sec


# ---------------------------
# TASK 2 → Live camera MJPEG stream (via WS)
# ---------------------------

async def stream_video():
    """
    Read either webcam frames or images from test_img folder
    and send via HTTP POST to server.
    """
    cap = cv2.VideoCapture(0)  # Use webcam
    image_files = [
        f for f in os.listdir(TEST_IMG_FOLDER)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    async with aiohttp.ClientSession() as session:
        while True:
            # Use webcam if available, else random test image
            ret, frame = cap.read()
            if not ret and image_files:
                # fallback to random image
                img_name = random.choice(image_files)
                frame = cv2.imread(os.path.join(TEST_IMG_FOLDER, img_name))
            elif not ret:
                # No webcam, no images
                await asyncio.sleep(0.1)
                continue

            # Resize to 480p
            frame = cv2.resize(frame, (640, 480))
            _, jpeg = cv2.imencode(".jpg", frame)
            jpeg_bytes = jpeg.tobytes()

            # Send via multipart/form-data
            data = aiohttp.FormData()
            data.add_field('file', jpeg_bytes, filename='frame.jpg', content_type='image/jpeg')

            try:
                await session.post(SERVER_UPLOAD_URL, data=data)
            except Exception as e:
                print(f"Error sending frame: {e}")

            await asyncio.sleep(0.03)  # ~30 FPS


async def main():
    await asyncio.gather(
        send_periodic_frames(),
        stream_video()
    )

if __name__ == "__main__":
    asyncio.run(main())





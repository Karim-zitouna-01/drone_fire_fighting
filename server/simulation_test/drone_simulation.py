import asyncio
import os
import random
import cv2
import websockets
import base64
import json
import socket

DRONE_ID = "2"

# -----------------------------
# UDP STREAM CONFIG
# -----------------------------
UDP_SERVER_IP = "127.0.0.1"
UDP_SERVER_PORT = 9999

TEST_IMG_FOLDER = "./test_img"

WS_FRAME_URL = f"ws://localhost:8000/ws/drone/{DRONE_ID}"


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
# TASK 1 → Telemetry every 20 sec (via WS)
# ---------------------------
async def send_periodic_frames():
    print("📡 Starting periodic telemetry sender...")

    image_files = [
        f for f in os.listdir(TEST_IMG_FOLDER)
        if f.lower().endswith((".jpg", ".png", ".jpeg"))
    ]

    if not image_files:
        print("❌ No images in test_img folder!")
        return

    async with websockets.connect(WS_FRAME_URL) as ws:
        print("✅ Connected to WS for telemetry.")

        while True:
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

            print(f"📤 Sent telemetry frame: {img_name}")
            await ws.send(json.dumps(payload))

            await asyncio.sleep(20)  # every 20 sec


# ---------------------------
# TASK 2 → Live MJPEG over UDP
# ---------------------------

async def stream_video_udp():
    """
    Read webcam frames or fallback images and send via UDP
    with header:  DRONE_ID|JPEG_BYTES
    """
    print("🎥 Starting UDP live stream... (ID:", DRONE_ID, ")")

    cap = cv2.VideoCapture(0)
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    image_files = [
        f for f in os.listdir(TEST_IMG_FOLDER)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    while True:
        ret, frame = cap.read()

        if not ret:
            if image_files:
                img_name = random.choice(image_files)
                frame = cv2.imread(os.path.join(TEST_IMG_FOLDER, img_name))
            else:
                await asyncio.sleep(0.1)
                continue

        frame = cv2.resize(frame, (640, 480))
        _, jpeg = cv2.imencode(".jpg", frame)
        jpeg_bytes = jpeg.tobytes()

        # -----------------------------
        # SEND FORMAT:  b"drone_id|JPEG_BYTES"
        # -----------------------------
        packet = DRONE_ID.encode() + b"|" + jpeg_bytes

        try:
            udp_socket.sendto(packet, (UDP_SERVER_IP, UDP_SERVER_PORT))
        except Exception as e:
            print("UDP send error:", e)

        await asyncio.sleep(0.03)  # ~30 FPS


# ---------------------------
# MAIN
# ---------------------------
async def main():
    await asyncio.gather(
        send_periodic_frames(),
        stream_video_udp()
    )


if __name__ == "__main__":
    asyncio.run(main())

from PIL import Image
import numpy as np
import cv2
import os
from ultralytics import YOLO


MODEL_PATH = "yolov5s_edgetpu.tflite"   # path to your compiled edgetpu model
IMAGE_PATH = "test.jpg"                 # path to image on your Pi
OUTPUT_PATH = "result.jpg"              # where to save the image with boxes
INPUT_SIZE = 640                        # common YOLO input size; if your model expects different, set it
CONF_THRESH = 0.4                       # confidence threshold
IOU_THRESH = 0.45                       # (not used by pycoral detect, but kept for reference)


# Load edgeTPU model
edgetpu_model = YOLO("yolov5su_full_integer_quant_edgetpu.tflite")


# Load and preprocess image
results = edgetpu_model(IMAGE_PATH)

# Process results
# Draw boxes on the image for detected persons
image = cv2.imread(IMAGE_PATH)
for result in results:
    for box in result.boxes:
        cls_id = int(box.cls[0])
        conf = box.conf[0]
        if cls_id == 0 and conf >= CONF_THRESH:  # class 0 is 'person' in COCO
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f"Person: {conf:.2f}"
            cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
# Save the output image
cv2.imwrite(OUTPUT_PATH, image)
print(f"Output saved to {OUTPUT_PATH}")



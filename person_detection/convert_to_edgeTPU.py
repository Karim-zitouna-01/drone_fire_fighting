#NB!! this operation is heavy, it's better ti run it on collab or similar environment

#installations
# !pip install torch torchvision
# !pip install ultralytics
# !pip install tensorflow
# !pip install pillow numpy opencv-python

from ultralytics import YOLO

# Load a pretrained YOLOv5 model (example: yolov5s) or custom .pt
model = YOLO("yolov5s.pt")  

# Export to TFLite -> edgeTPU
model.export(format="edgetpu")

print("TFLite model exported successfully!")

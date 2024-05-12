from ultralytics import YOLO

# Load a pretrained YOLOv8n model
model = YOLO('best (9).pt')

# Run inference on 'bus.jpg' with arguments
# model = yolov8()

# Perform inference
results = model('captured_image.jpg')

for result in results:
    if result.boxes:
        box = result.boxes[0]
        class_id = int(box.cls)
        object_name = model.names[class_id]
        print(object_name)
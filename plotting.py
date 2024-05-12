import cv2
from ultralytics import YOLO
img_pth = "captured_image.jpg"
model = YOLO("best (8).pt") 
results = model(source=img_pth)
res_plotted = results[0].plot()
cv2.imwrite("result.jpg", res_plotted)
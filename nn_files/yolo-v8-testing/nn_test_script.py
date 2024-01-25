from ultralytics import YOLO
import numpy as np
import cv2
import depthai
from time import time
import torch

# Load the YOLOv8 models
model = YOLO('best_v2.pt')

cap = cv2.VideoCapture(0)

# Check if the webcam is opened correctly
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

try:
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        # If frame is read correctly, ret is True
        if not ret:
            print("Error: Can't receive frame (stream end?). Exiting ...")
            break
        
        resized_frame = cv2.resize(frame, (640, 640))
        results = model(resized_frame)
        annotated_frame = results[0].plot()

        # Display the resulting frame
        cv2.imshow('Webcam Frame', annotated_frame)
        #cv2.imshow('Webcam Frame', frame)

        # Press 'q' on the keyboard to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    # When everything is done, release the capture
    cap.release()
    cv2.destroyAllWindows()
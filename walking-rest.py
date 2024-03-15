import cv2
import asyncio
import random
import json
import time
from flask import Flask, request, jsonify
from ultralytics import YOLO
import base64
import os
import threading
import supervision as sv

app = Flask(__name__)

# Initialize the YOLO model
model = None

def initialize_model():
    global model
    os.environ['YOLO_VERBOSE'] = 'False'
    model = YOLO('custom-models/walking-model.pt', verbose=False)

# Function to perform object detection and update shared data
class UltrasonicSensor:
    def measure_distance(self):
        # Simulate measuring distance (replace this with actual sensor reading)
        return random.uniform(0, 100)

box_annotator = sv.BoxAnnotator(
        thickness=2,
        text_thickness=2,
        text_scale=1
    )  
def perform_detection(shared_data):
    vc = cv2.VideoCapture(0)
    vc.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    vc.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    if not vc.isOpened():
        print("Error: Couldn't open webcam.")
        return

    ultrasonic_sensor = UltrasonicSensor()  # Initialize your ultrasonic sensor here

    while True:
        rval, frame = vc.read()
        if not rval:
            print("Error: Couldn't read frame.")
            break
        
        results = model(frame)[0]
        detections = sv.Detections.from_ultralytics(results)
        door_detections = detections[detections.class_id == 0]
        # frame = box_annotator.annotate(
        #     scene=frame, 
        #     detections=door_detections,
            
        # )
        cv2.imshow("yolov8", frame)
        
        if len(door_detections) > 0 and door_detections[door_detections.confidence > 0.9]:
            # Perform distance calculation
            distance = ultrasonic_sensor.measure_distance()  # Example function, replace with your own implementation
            shared_data['object_detected'] = True
            shared_data['distance'] = distance
        else:
            shared_data['object_detected'] = False

        # Sleep for a while to control the detection rate
        # time.sleep(1)

# Background task to perform detection continuously
def background_task(shared_data):
    while True:
        perform_detection(shared_data)

# API endpoint for clients to get updates
@app.route('/get_update', methods=['GET'])
def get_update():
    global shared_data
    return jsonify({'object_detected': shared_data.get('object_detected', False),
                    'distance': shared_data.get('distance', None)})

if __name__ == '__main__':
    # Initialize the model
    initialize_model()

    # Shared data between detection task and API endpoint
    shared_data = {'object_detected': False, 'distance': None}

    # Start the background task
    detection_thread = threading.Thread(target=background_task, args=(shared_data,))
    detection_thread.daemon = True
    detection_thread.start()

    # Run the Flask app
    app.run(host='0.0.0.0', port=9001)

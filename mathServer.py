import json
import cv2
import threading
from ultralytics import YOLO
import logging
import supervision as sv

class MathDetectionServer:
    def __init__(self):
        self.active = False
        self.client = None
        self.server = None
        self.thread = None

    def run(self, client, server, message):
        self.client = client
        self.server = server
        data = json.loads(message)
        command = data.get("command")

        if command == "start":
            if not self.active:
                self.active = True
                self.start_detection()
        elif command == "stop":
            self.stop_detection()

    def start_detection(self):
        if self.thread is None or not self.thread.is_alive():
            self.initialize_resources()
            self.thread = threading.Thread(target=self.detect)
            self.thread.start()

    def initialize_resources(self):
        self.cap = cv2.VideoCapture(0)
        self.yolo = YOLO("models/math-model.pt")
        logging.info("Detection resources initialized")

    def detect(self):
     while self.active:
        success, frame = self.cap.read()
        if success:
            results = self.yolo(frame)[0]
            detections = sv.Detections.from_ultralytics(results)  # Modify as needed
            detections = detections[detections.confidence > 0.30]
            print(detections)
            if len(detections) == 1:
                    labels = ""
                    if detections[detections.class_id == 0]:
                        labels = "circle"
                    elif detections[detections.class_id == 1]:
                        labels = "cube"
                    elif detections[detections.class_id == 2]:
                        labels = "cylinder"
                    elif detections[detections.class_id == 3]:
                        labels = "triangle"
                    
                    detection_message = {"type": "detection", "message": "Object detected!", "detections": labels }
                    self.server.send_message(self.client, json.dumps(detection_message))
                    self.active = False  # Set active to False to stop detection
                    break  # Exit the loop to end the thread

     self.release_resources()


    def stop_detection(self):
        self.active = False
        # Send stop message to client
        stop_message = {"type": "info", "message": "Detection stopped"}
        self.server.send_message(self.client, json.dumps(stop_message))

    def release_resources(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
        logging.info("Detection resources released")

    def reset(self):
        self.active = False
        self.release_resources()
        self.thread = None
        logging.info("Server reset for next start")

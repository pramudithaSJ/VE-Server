import json
import cv2
import threading
from ultralytics import YOLO
import logging
import supervision as sv

class ScienceDetectionServer:
    def __init__(self):
        self.active = False
        self.client = None
        self.server = None
        self.thread = None
        print("Science Detection Server initialized")

    def run(self, client, server, message):
        print("Science Detection Server run method called")
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
        self.model = YOLO("models/best65.pt")
        logging.info("Detection resources initialized")

    def detect(self):
     while self.active:
            success, frame = self.cap.read()
            if not success:
                logging.error("Failed to read frame from camera")
                self.release_resources()

            results = self.model(frame)
            logging.info(f"YOLO results: {results}")

            detections = results[0].boxes
            high_conf_detections = [det for det in detections if det.conf.item() > 0.60]
            logging.info(f"High confidence detections: {high_conf_detections}")

            if high_conf_detections:
                logging.info("High confidence detections found")
                labels = [self.model.names[int(det.cls.item())] for det in high_conf_detections]
                detection_message = {"type": "detection", "message": "Object detected!", "detections": labels}
                self.server.send_message(self.client, json.dumps(detection_message))
                self.active = False
                self.release_resources()
                self.stop_detection()

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

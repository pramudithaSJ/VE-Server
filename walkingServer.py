import json
import cv2
import threading
from ultralytics import YOLO
import logging
import supervision as sv

class WalkingServer:
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
        self.yolo = YOLO("models/best8n_ncnn_model")
        logging.info("Detection resources initialized")

    def detect(self):
        while self.active:
            success, frame = self.cap.read()
            if success:
                results = self.yolo(frame)[0]
                detections = sv.Detections.from_ultralytics(results)
                detections = detections[detections.class_id == 0]
                if len(detections) > 0:
                    if detections[detections.confidence > 0.75]:
                        warning_message = {"type": "warning", "message": "Door detected!","distance":"11"}
                        self.server.send_message(self.client, json.dumps(warning_message))
                    else:
                        warning_message = {"type": "safe", "message": "No door detected!"}
                        self.server.send_message(self.client, json.dumps(warning_message))
                else:
                    warning_message = {"type": "safe", "message": "No door detected!"}
                    self.server.send_message(self.client, json.dumps(warning_message))
     
        self.release_resources()

    def stop_detection(self):
        self.active = False
        if self.thread is not None:
            self.thread.join()
        self.release_resources()

    def release_resources(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
        logging.info("Detection resources released")

    def reset(self):
        self.active = False
        self.release_resources()
        self.thread = None
        logging.info("Server reset for next start")

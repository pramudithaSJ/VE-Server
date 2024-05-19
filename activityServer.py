import json
import cv2
import threading
from ultralytics import YOLO
import logging
import supervision as sv

class ActivityServer:
    def __init__(self):
        self.active = False
        self.client = None
        self.server = None
        self.thread = None
        self.detected_notes = []
        self.json_sink_path = "detected_notes.json"

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
        elif command == "finished":
            self.calculate_total()

    def start_detection(self):
        if self.thread is None or not self.thread.is_alive():
            self.initialize_resources()
            self.thread = threading.Thread(target=self.detect)
            self.thread.start()

    def initialize_resources(self):
        self.cap = cv2.VideoCapture(0)
        self.yolo = YOLO("models/activity.pt")
        logging.info("Detection resources initialized")

    def detect(self):
        with sv.JSONSink(self.json_sink_path) as sink:
            while self.active:
                success, frame = self.cap.read()
                if success:
                    results = self.yolo(frame)[0]
                    detections = sv.Detections.from_ultralytics(results)
                    detections = detections[detections.confidence > 0.70]
                    print(detections)
                    if len(detections) > 0:
                        labels = [
                            f"{class_name} {confidence:.2f}"
                            for class_name, confidence
                            in zip(detections['class_name'], detections.confidence)
                        ]
                        detection_message = {"type": "detection", "message": "Object detected!", "detections": labels}
                        self.server.send_message(self.client, json.dumps(detection_message))

                        # Store detected notes
                        for class_name in detections['class_name']:
                            self.detected_notes.append(class_name)

                        # Save detections to JSON
                        sink.append(detections, {"frame_index": frame})

        self.release_resources()

    def release_resources(self):
        if self.cap.isOpened():
            self.cap.release()
        self.yolo.close()
        logging.info("Detection resources released")

    def stop_detection(self):
        self.active = False
        self.release_resources()
        stop_message = {"type": "info", "message": "Detection stopped"}
        self.server.send_message(self.client, json.dumps(stop_message))

    def calculate_total(self):
        # Define the value of each note (assuming the class names correspond to note values)
        note_values = {
            '10': 10,
            '20': 20,
            '50': 50,
            '100': 100,
            '500': 500,
            '1000': 1000,
            '2000': 2000,
            '5000': 5000
        }

        total_amount = sum(note_values[note] for note in self.detected_notes if note in note_values)

        total_message = {"type": "total", "message": "Total amount calculated", "total_amount": total_amount}
        self.server.send_message(self.client, json.dumps(total_message))

        # Reset detected notes for the next session
        self.detected_notes = []



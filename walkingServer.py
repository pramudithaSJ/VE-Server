import json
import cv2
import threading
from ultralytics import YOLO
import logging
import supervision as sv
import RPi.GPIO as GPIO
import time

TRIG_PIN = 21
ECHO_PIN = 20

# Set up GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

class UltrasonicSensor:
    @staticmethod
    def get_distance():
        # Ensure the trigger pin is low
        GPIO.output(TRIG_PIN, False)
        time.sleep(0.2)  # Delay to ensure sensor settles

        # Trigger ultrasonic pulse
        GPIO.output(TRIG_PIN, True)
        time.sleep(0.00001)
        GPIO.output(TRIG_PIN, False)

        # Measure time for echo
        pulse_start = None
        pulse_end = None

        # Wait for the echo to start
        timeout_start = time.time()
        while GPIO.input(ECHO_PIN) == 0:
            pulse_start = time.time()
            if time.time() - timeout_start > 0.1:  # Timeout after 0.1 seconds
                print("Timeout: No echo start detected")
                return None

        # Wait for the echo to end
        timeout_start = time.time()
        while GPIO.input(ECHO_PIN) == 1:
            pulse_end = time.time()
            if time.time() - timeout_start > 0.1:  # Timeout after 0.1 seconds
                print("Timeout: No echo end detected")
                return None

        if pulse_start is None or pulse_end is None:
            print("Failed to detect echo")
            return None

        # Calculate distance in cm
        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150
        distance = round(distance, 2)
        return distance
    

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
                    high_confidence_detections = detections[detections.confidence > 0.75]
                    if len(high_confidence_detections) > 0:
                        # Wait for the distance measurement
                        distance = UltrasonicSensor.get_distance()
                        # distance = 10
                        if distance is not None:
                            warning_message = {
                                "type": "warning", 
                                "message": "Door detected!",
                                "distance": distance
                            }
                        else:
                            warning_message = {
                                "type": "warning", 
                                "message": "Door detected! (Distance measurement failed)"
                            }
                        self.server.send_message(self.client, json.dumps(warning_message))
                    else:
                        safe_message = {"type": "safe", "message": "No door detected!"}
                        self.server.send_message(self.client, json.dumps(safe_message))
                else:
                    safe_message = {"type": "safe", "message": "No door detected!"}
                    self.server.send_message(self.client, json.dumps(safe_message))

        self.release_resources()


    def stop_detection(self):
        self.active = False
        if self.thread is not None:
            self.thread.join()
        self.release_resources()
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

import cv2
import asyncio
import random
import json
import threading
from ultralytics import YOLO
from websocket_server import WebsocketServer
import base64
import os
import supervision as sv


def set_yolo_verbose_false():
    # Set the environment variable YOLO_VERBOSE to 'False'
    os.environ['YOLO_VERBOSE'] = 'False'
    print("YOLO_VERBOSE set to False")

# Example usage
set_yolo_verbose_false()

# Load the YOLO model
model = YOLO('custom-models/walking-model.pt',verbose=False)

def new_client(client, server):
    print(f"New client connected: {client['id']}")

# Function to handle client disconnections
def client_left(client, server):
    print(f"Client disconnected: {client['id']}")
    
def send_detection_to_clients(detections, server):
    try:
        detection_data = json.dumps(detections)
        server.send_message_to_all(detection_data)
        asyncio.sleep(10)
    except:
        pass
server = WebsocketServer(host ="0.0.0.0",port=9001)
server.set_fn_new_client(new_client)
server.set_fn_client_left(client_left)
threading.Thread(target=server.run_forever).start()


async def detect_doors(): 
    vc = cv2.VideoCapture(0)
    vc.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    vc.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    if not vc.isOpened():
        print("Error: Couldn't open webcam.")
        return
    
    while True:
        rval, frame = vc.read()
        if not rval:
            print("Error: Couldn't read frame.")
            break
        
        results = model(frame)[0]
        detections = sv.Detections.from_ultralytics(results)
        detections = detections[detections.class_id == 0]
        
        if len(detections) > 0:
            if detections[detections.confidence > 0.9]:
                warning_message = {"type": "warning", "message": "Door detected!","distance": 10.0}
                send_detection_to_clients(warning_message, server)
        else:
            safe_message = {"type": "safe", "message": "No door detected."}
            send_detection_to_clients(safe_message, server)   
    

async def main():
    await detect_doors()
    
    
asyncio.run(main())

